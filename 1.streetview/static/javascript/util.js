function StreetviewService(){
  return {
    find_target_for_event: function(event){
      var target = null;
      if (event.target) {
        target = event.target;
      } else if (event.srcElement) {
        target = event.srcElement;
      } else {
        alert('unexpected lack of taget for event: ' + event);
      }
      return target;
    },
  }
}
