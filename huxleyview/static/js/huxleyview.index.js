Huxleyview.Controllers.document = {
  'ready': function(event){
    Huxleyview.Request.GetAllTcaseRunTimes();
    Huxleyview.Request.GetLatestTcase();
  },
};

Huxleyview.Controllers['#tcase-timeline'] = {
  'refreshTimeline':function(event){
    Huxleyview.UI.RefreshTimeline();
  },
};

Huxleyview.Controllers['#tcase-list'] = {
  'refreshTcaseList':function(event){
    Huxleyview.UI.RefreshTcaseList();
  },
};

var components = [
  {id: 'document', event:'ready'},
  {id: '#tcase-timeline', event:'refreshTimeline'},
  {id: '#tcase-list', event:'refreshTcaseList'},
];

Huxleyview.Run(components);
