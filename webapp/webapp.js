//
// Client & Server
//

HAT = 'hat';

Devices = new Meteor.Collection('devices');


//
// Server only
//

if (Meteor.isServer) {
  // Bootstrap collection with a device if there are
  // none in there already.
  if (Devices.find().count() === 0) {
    Devices.insert({
      _id: HAT,
      isActivated: false
    });
  }
}


//
// Client only
//

if (Meteor.isClient) {
  var setHatState = function (isActivated) {
    Devices.update(HAT, {
      isActivated: isActivated
    });
  };

  var isHatActivated = function () {
    var hat = Devices.findOne(HAT);
    return hat && hat.isActivated;
  };

  Template.controller.helpers({
    active: function () {
      if (isHatActivated()) {
        return 'active';
      }
    },
    buttonSuffix: function () {
      return isHatActivated() ? 'on' : 'off';
    }
  });

  Template.controller.events({
    'click #party-hat': function (event) {
      event.preventDefault();
      setHatState(!isHatActivated());
    }
  });
}

