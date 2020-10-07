PlanItPokerNewmanReporter = function (newman, reporterOptions, collectionRunOptions) {
  newman.on('request', function(err, args) {
      var issues = args.response.json().issues;
      issues.forEach(issue => console.log('[' + issue.key + '] ' + issue.fields.summary.replace(',', ':') + '\''));
  });
};

module.exports = PlanItPokerNewmanReporter;
