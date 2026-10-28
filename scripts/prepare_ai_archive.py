#!/usr/bin/env python3
"""Recover project-specific visible AI dialogue and tool traces; omit hidden reasoning."""
from pathlib import Path
import datetime, json, re, shlex, shutil, zipfile
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'submission/ai'
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'records').mkdir(exist_ok=True)
secrets=[]
for line in (ROOT/'.env').read_text().splitlines():
    if '=' not in line or line.lstrip().startswith('#'):continue
    k,v=line.split('=',1)
    if re.search(r'PASSWORD|TOKEN|SECRET',k,re.I):
        try:v=shlex.split(v)[0]
        except (ValueError,IndexError):continue
        if len(v)>3:secrets.append(v)

def redact(s):
    for v in secrets:s=s.replace(v,'[REDACTED CREDENTIAL]')
    s=re.sub(r'\b(?:gh[pousr]_[A-Za-z0-9_]{15,}|github_pat_[A-Za-z0-9_]{15,}|sk-[A-Za-z0-9_-]{20,})','[REDACTED TOKEN]',s)
    s=re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+','[BINARY IMAGE OMITTED]',s)
    s=re.sub(r'(https://docs.google.com/docs-images-rt/[^\s)]+)','[TEMPORARY DOCUMENT IMAGE URL OMITTED]',s)
    return s

def visible(s):
    s=re.sub(r'<system-reminder>.*?</system-reminder>','',s,flags=re.S)
    return s.strip()

dialogues={'codex':[],'claude_code':[]}; index=[]
for p in sorted(Path('/Users/hikaru/.codex/sessions').rglob('*.jsonl')):
    try:
        with p.open() as f:first=json.loads(f.readline())
        cwd=first.get('payload',{}).get('cwd','')
        if cwd!=str(ROOT) and not cwd.startswith(str(ROOT)+'/'):continue
    except Exception:continue
    rows=[];narrative=[];approval=False
    for line in p.open():
        try:a=json.loads(line)
        except ValueError:continue
        if a.get('type')!='response_item':continue
        v=a.get('payload',{});kind=v.get('type')
        if kind=='message' and v.get('role') in ['user','assistant']:
            if v.get('channel')=='analysis':continue
            t='\n'.join(c.get('text','') for c in v.get('content',[]) if c.get('type') in ['input_text','output_text','text'])
            if t.startswith('The following is the Codex agent history'):approval=True;break
            if t.startswith(('<environment_context>','<external_codex_apps_open_page>','<send_user_message_question_reply>')):continue
            if t.strip():
                entry=dict(timestamp=a.get('timestamp'),role=v['role'],text=redact(t));rows.append(entry);narrative.append(entry)
        elif kind in ['function_call','function_call_output','custom_tool_call','custom_tool_call_output']:
            # Reasoning and application/system metadata never enter the export.
            rows.append(json.loads(redact(json.dumps(dict(timestamp=a.get('timestamp'),record=v),ensure_ascii=False))))
    if approval or not narrative:continue
    name='codex-'+p.stem+'.jsonl'
    (OUT/'records'/name).write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
    dialogues['codex'].append((p.stem,narrative))
    index.append(dict(tool='Codex',session=p.stem,visible_messages=len(narrative),exported_records=len(rows),record='records/'+name))

for folder in Path('/Users/hikaru/.claude/projects').glob('*cs5424-distributed-database*'):
    for p in sorted(folder.rglob('*.jsonl')):
        rows=[];narrative=[]
        for line in p.open():
            try:a=json.loads(line)
            except ValueError:continue
            if a.get('type') not in ['user','assistant']:continue
            message=a.get('message',{});c=message.get('content',[])
            if isinstance(c,str):c=[dict(type='text',text=c)]
            for block in c:
                if not isinstance(block,dict):continue
                if block.get('type')=='text':
                    t=visible(block.get('text',''))
                    if t:
                        entry=dict(timestamp=a.get('timestamp'),role=a['type'],text=redact(t));rows.append(entry);narrative.append(entry)
                elif block.get('type') in ['tool_use','tool_result']:
                    rows.append(json.loads(redact(json.dumps(dict(timestamp=a.get('timestamp'),record=block),ensure_ascii=False))))
        if not narrative:continue
        name='claude-'+p.stem+'.jsonl'
        (OUT/'records'/name).write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
        dialogues['claude_code'].append((p.stem,narrative))
        index.append(dict(tool='Claude Code',session=p.stem,visible_messages=len(narrative),exported_records=len(rows),record='records/'+name))

font='/Library/Fonts/Arial Unicode.ttf'
pdfmetrics.registerFont(TTFont('RecordSans',font))
style=ParagraphStyle('Body',fontName='RecordSans',fontSize=10,leading=13,spaceAfter=6,splitLongWords=True)
heading=ParagraphStyle('Heading',parent=style,fontSize=16,leading=20,spaceBefore=12,spaceAfter=12)
label=ParagraphStyle('Label',parent=style,fontSize=10,leading=13,textColor=colors.HexColor('#334155'),spaceBefore=8)

def safe_pdf(s):
    return ''.join(c if ord(c)<=0xffff else '[U+%X]'%ord(c) for c in s)

def footer(canvas,doc):
    canvas.setFont('RecordSans',9)
    canvas.drawString(42,25,'Team 14 AI interaction record')
    canvas.drawRightString(A4[0]-42,25,str(doc.page))

for tool,sessions in dialogues.items():
    story=[Paragraph('Team 14 '+('Codex' if tool=='codex' else 'Claude Code')+' usage and interaction record',heading)]
    overview=('This record documents recovered project-specific prompts and visible assistant responses. '
        'Codex assisted with implementation, validation, cluster evidence review, documentation, report preparation and packaging. '
        'Claude Code assisted with follow-up A experiments, cluster runs, validation and evidence analysis as recorded below. '
        'The team is responsible for understanding and checking the submitted work. '
        'Hidden reasoning and system/developer instructions are excluded. Private credentials and temporary authenticated image URLs are redacted. '
        'Supplemental JSONL files preserve the recovered visible dialogue and tool call/result records. '
        'These local archives may not cover earlier cloud/ChatGPT conversations or other members\' AI use; those records must be supplied before final submission. '
        'This is a preparation snapshot, not a claim that the team-wide AI record is complete.')
    story.append(Paragraph(escape(overview),style))
    story.append(Paragraph('Recovered sessions: '+str(len(sessions))+'. Prepared '+datetime.datetime.now(datetime.timezone.utc).isoformat()+'.',style))
    for session,messages in sessions:
        story.append(PageBreak());story.append(Paragraph('Session '+escape(session),heading))
        for entry in messages:
            story.append(Paragraph(escape(entry['role'].upper()+' | '+str(entry.get('timestamp') or 'timestamp unavailable')),label))
            # Break prose into bounded paragraphs for deterministic page flow.
            for paragraph in entry['text'].split('\n\n'):
                for start in range(0,len(paragraph),1800):
                    s=safe_pdf(paragraph[start:start+1800]);s=re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]',' ',s)
                    story.append(Paragraph(escape(s).replace('\n','<br/>'),style))
    SimpleDocTemplate(str(OUT/f'14_{tool}_interactions.pdf'),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=42).build(story,onFirstPage=footer,onLaterPages=footer)

(OUT/'session-index.json').write_text(json.dumps(index,indent=2)+'\n')
(OUT/'README.txt').write_text('Team 14 AI archive review snapshot\n\nPDFs include recovered project-session user prompts and visible assistant responses. JSONL records additionally retain recovered tool inputs/outputs. Hidden reasoning and system/developer metadata are excluded; credentials are redacted.\n\nCompleteness is NOT established: obtain earlier 10/14/15/19 October cloud/ChatGPT interactions if absent here, and all teammates\' records and declarations. Re-run this script after the last project interaction. The active conversation is captured only through the moment the script reads it.\n')
shutil.copy2(ROOT/'AI_USAGE.md',OUT/'14_ai_usage_index.md')
target=ROOT/'submission/upload/14_ai_tool.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(OUT.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(OUT))
with zipfile.ZipFile(target) as z:assert z.testzip() is None
print('AI archive:',len(index),'sessions;',sum(x['visible_messages'] for x in index),'visible messages;',target.stat().st_size,'bytes')
