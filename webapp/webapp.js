var HAT = 'hat';

var Devices = new Meteor.Collection('devices');

if (Meteor.isServer) {
  if (Devices.find().count() === 0) {
    Devices.insert({
      _id: HAT,
      isActivated: false
    });
  }
}

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

