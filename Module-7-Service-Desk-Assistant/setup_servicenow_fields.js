/**
 * setup_servicenow_fields.js
 *
 * HOW TO RUN:
 *   1. Log in to https://your-instance.service-now.com
 *   2. Filter navigator (top-left) → type:  scripts.do  → Enter
 *   3. Paste this entire file into the editor
 *   4. Click  "Run Script"  (top-right)
 *   5. Read the output log — each field prints CREATED or SKIP
 *
 * Safe to run multiple times — skips fields that already exist.
 */

var FIELDS = [
  { column_name: 'u_ai_root_cause_hypothesis',  column_label: 'AI Root Cause Hypothesis',  internal_type: 'string',  max_length: 1000 },
  { column_name: 'u_ai_evidence_summary',        column_label: 'AI Evidence Summary',        internal_type: 'string',  max_length: 4000 },
  { column_name: 'u_ai_suspect_commit',          column_label: 'AI Suspect Commit',          internal_type: 'string',  max_length: 100  },
  { column_name: 'u_ai_suspect_deployment',      column_label: 'AI Suspect Deployment',      internal_type: 'string',  max_length: 100  },
  { column_name: 'u_ai_confidence_score',        column_label: 'AI Confidence Score',        internal_type: 'integer', max_length: null },
  { column_name: 'u_ai_recommended_next_step',   column_label: 'AI Recommended Next Step',   internal_type: 'string',  max_length: 500  },
  { column_name: 'u_ai_evidence_gaps',           column_label: 'AI Evidence Gaps',           internal_type: 'string',  max_length: 500  },
  { column_name: 'u_ai_investigation_lock',      column_label: 'AI Investigation Lock',      internal_type: 'string',  max_length: 200  },
  { column_name: 'u_ai_investigation_status',    column_label: 'AI Investigation Status',    internal_type: 'string',  max_length: 50   }
];

var TABLE_NAME = 'incident';
var created = 0, skipped = 0, errors = 0;

gs.print('============================================================');
gs.print(' Creating AI Root-Cause Investigation fields on: ' + TABLE_NAME);
gs.print('============================================================');

for (var i = 0; i < FIELDS.length; i++) {
  var f = FIELDS[i];

  // Skip if already exists
  var existing = new GlideRecord('sys_dictionary');
  existing.addQuery('name', TABLE_NAME);
  existing.addQuery('element', f.column_name);
  existing.query();
  if (existing.next()) {
    gs.print('SKIP   [' + (i+1) + '/9] ' + f.column_name + ' — already exists');
    skipped++; continue;
  }

  // Create the field
  var dict = new GlideRecord('sys_dictionary');
  dict.initialize();
  dict.setValue('name',          TABLE_NAME);
  dict.setValue('element',       f.column_name);
  dict.setValue('column_label',  f.column_label);
  dict.setValue('internal_type', f.internal_type);
  dict.setValue('active',        true);
  dict.setValue('mandatory',     false);
  dict.setValue('read_only',     false);
  if (f.max_length !== null) { dict.setValue('max_length', f.max_length); }

  var sysId = dict.insert();
  if (sysId) {
    gs.print('CREATED [' + (i+1) + '/9] ' + f.column_name + '  (' + f.internal_type + ', max=' + (f.max_length || 'n/a') + ')');
    created++;
  } else {
    gs.print('ERROR   [' + (i+1) + '/9] ' + f.column_name);
    errors++;
  }
}

gs.print('============================================================');
gs.print(' DONE  Created:' + created + '  Skipped:' + skipped + '  Errors:' + errors);
gs.print('============================================================');
