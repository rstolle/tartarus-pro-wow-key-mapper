const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '..', 'tartarus-wow.html'), 'utf8');
const scripts = [...html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)];
const code = scripts.find(([, attrs]) => !attrs.includes('application/json'))[2];
new vm.Script(code);
const data = id => JSON.parse(scripts.find(([, attrs]) => attrs.includes(`id="${id}"`))[2]);
const library = data('spell-data');
assert.equal(data('saved-data'), null, 'Published source must have no personal layouts');
assert.equal(new Set(library.spells.map(s => s.id)).size, library.spells.length);
for (const spell of library.spells) {
  assert.ok(Object.hasOwn(library.catalogs, spell.flavor));
  assert.ok(Object.hasOwn(library.icons, spell.icon));
  assert.ok(spell.level === null || (Number.isInteger(spell.level) && spell.level > 0));
}
const root = {dataset: {}, querySelector: () => ({textContent: ''}), querySelectorAll: () => []};
const context = {
  LIBRARY: library, assert,
  document: {
    documentElement: root, querySelectorAll: () => [],
    getElementById: id => ({textContent: id === 'storage-id' ? '"original"' : '"forever"'})
  }
};
// Exercise the app's actual data model without browser rendering.
vm.runInNewContext(code.slice(code.indexOf('const CLASSES'), code.indexOf("let loadMessage='';")) +
  code.slice(code.indexOf('const profile ='), code.indexOf('const spellById')) +
  code.match(/function spellAvailable\(spell\)\{[^\n]+\}/)[0] + `
const legacy=initialState();delete legacy.profiles[0].flavor;delete legacy.flavorProfiles;
legacy.profiles[0].layers.base['01']={spellId:LIBRARY.spells.find(s=>s.flavor==='forever').id,note:'Old save'};
legacy.customSkills.push({id:'legacy-custom',name:'Legacy macro',class:'Mage',icon:''});
let migrated=validateState(legacy);
assert.equal(migrated.librarySort,'name');
migrated.librarySort='level';
assert.equal(migrated.profiles[0].flavor,'forever');
assert.equal(migrated.customSkills[0].flavor,'forever');
assert.equal(migrated.profiles[0].layers.base['01'].note,'Old save');
for(const f of ['retail','classic','forever']){
  const p=newProfile(f,'Mage',f);
  p.layers.base['01']={spellId:LIBRARY.spells.find(s=>s.flavor===f&&s.class==='Mage').id,note:''};
  migrated.profiles.push(p);migrated.flavorProfiles[f]=p.id;
}
migrated.activeProfile=migrated.flavorProfiles.retail;
migrated=validateState(migrated);
assert.deepEqual(validateState(JSON.parse(JSON.stringify(migrated))),migrated);
state=migrated;
assert.ok(spellAvailable(LIBRARY.spells.find(s=>s.flavor==='retail')));
assert.ok(!spellAvailable(LIBRARY.spells.find(s=>s.flavor==='forever')));
migrated.profiles[0].layers.base['01'].spellId=LIBRARY.spells.find(s=>s.flavor==='retail').id;
assert.throws(()=>validateState(migrated),'Cross-flavor assignment must fail');
assert.equal(flavorClasses('retail').length,14);
assert.equal(flavorClasses('classic').length,12);
assert.equal(flavorClasses('forever').length,10);
assert.ok(!flavorClasses('classic').includes('Evoker'));
assert.ok(!flavorClasses('forever').includes('Monk'));
const sample=[
  {id:'1',class:'Mage',name:'Alpha',level:10},
  {id:'2',class:'Mage',name:'Zulu',level:2},
  {id:'3',class:'Mage',name:'Beta',level:2},
  {id:'4',class:'Mage',name:'Unknown',level:null},
  {id:'5',class:'Mage',name:'Custom',custom:true}
];
assert.equal([...sample].sort((a,b)=>compareSpells(a,b,'level')).map(s=>s.id).join(','),'3,2,1,5,4');
assert.equal([...sample].sort((a,b)=>compareSpells(a,b,'name')).map(s=>s.id).join(','),'1,3,5,4,2');
assert.equal(spellLevel({level:0}),null);
assert.equal(spellLevel({level:'10'}),null);
`, context);
console.log('PASS: catalog integrity, save migration, flavor isolation, numeric/name sorting, unknown levels, and backup roundtrip.');
