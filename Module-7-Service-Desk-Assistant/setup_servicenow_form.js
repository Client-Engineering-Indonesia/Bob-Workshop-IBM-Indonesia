/**
 * setup_servicenow_form.js
 *
 * HOW TO RUN — after setup_servicenow_fields.js has completed:
 *   Filter navigator → scripts.do → paste → Run Script
 *
 * Adds all 9 AI fields to a new "AI Root-Cause Investigation" section
 * at the bottom of the default Incident form view.
 */

var TABLE_NAME   = 'incident';
var SECTION_NAME = 'AI Root-Cause Investigation';
var AI_FIELDS    = [
  'u_ai_investigation_status',
  'u_ai_root_cause_hypothesis',
  'u_ai_confidence_score',
  'u_ai_recommended_next_step',
  'u_ai_suspect_commit',
  'u_ai_suspect_deployment',
  'u_ai_evidence_summary',
  'u_ai_evidence_gaps',
  'u_ai_investigation_lock'
];

gs.print('============================================================');
gs.print(' Adding AI section to Incident form');
gs.print('============================================================');

// Find a view for the incident table
var viewGr = new GlideRecord('sys_ui_view');
viewGr.addQuery('table_name', TABLE_NAME);
viewGr.query();

if (!viewGr.next()) {
  gs.print('ERROR: No view found for ' + TABLE_NAME + ' — add fields manually via Form Layout');
} else {
  var viewId = viewGr.getUniqueValue();
  gs.print('Found view: ' + viewGr.getValue('name') + '  (' + viewId + ')');

  // Check section doesn't already exist
  var existSec = new GlideRecord('sys_ui_section');
  existSec.addQuery('view', viewId);
  existSec.addQuery('caption', SECTION_NAME);
  existSec.query();
  var secId;
  if (existSec.next()) {
    secId = existSec.getUniqueValue();
    gs.print('Section already exists — reusing (' + secId + ')');
  } else {
    var sec = new GlideRecord('sys_ui_section');
    sec.initialize();
    sec.setValue('view', viewId); sec.setValue('table', TABLE_NAME);
    sec.setValue('caption', SECTION_NAME); sec.setValue('position', 20); sec.setValue('columns', 1);
    secId = sec.insert();
    gs.print('Created section: "' + SECTION_NAME + '"  (' + secId + ')');
  }

  // Add each field
  for (var i = 0; i < AI_FIELDS.length; i++) {
    var el = new GlideRecord('sys_ui_element');
    el.initialize();
    el.setValue('view', viewId); el.setValue('section', secId);
    el.setValue('element', AI_FIELDS[i]); el.setValue('position', i); el.setValue('column', 0);
    var eid = el.insert();
    gs.print((eid ? 'ADDED  ' : 'FAILED ') + '[' + (i+1) + '/9] ' + AI_FIELDS[i]);
  }

  gs.print('============================================================');
  gs.print(' DONE — open any Incident and scroll to bottom to confirm');
  gs.print('============================================================');
}
