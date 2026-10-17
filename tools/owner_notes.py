"""Keep the owner's exported edits when source data is rebuilt."""
import json

def read_owner_notes(folder):
 result={}
 for path in folder.glob('*.json'):
  if path.name=='catalog.json':continue
  for unit in json.loads(path.read_text(encoding='utf-8')).get('units',[]):
   if unit.get('reading',{}).get('ownerEdited'):result[unit['id']]=unit
 return result

def restore_owner_notes(unit,saved):
 old=saved.get(unit['id'])
 if old and (old['ref'],old['greek'])==(unit['ref'],unit['greek']):
  unit['reading']={**unit['reading'],**{k:old['reading'][k] for k in ('zh','de','structure')},'ownerEdited':True}
  unit['reading'].pop('alignment',None)
 return unit
