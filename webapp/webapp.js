var HAT = 'hat';

var Devices = new Meteor.Collection('devices');

Meteor.methods({
  'activateHat': function () {
    setHatState(true);
  },

  'deactivateHat': function () {
    setHatState(false);
  }
});

var setHatState = function (isActivated) {
  Devices.upsert({
    name: HAT
  }, {
    name: HAT,
    isActivated: isActivated
  });
};

if (Meteor.isClient) {
  Template.controller.helpers({
    buttonSuffix: function () {
      return isHatActivated() ? 'off' : 'on';
    }
  });

  Template.controller.events({
    'click #led': function (event) {
      event.preventDefault();
      if (isHatActivated()) {
        Meteor.call('deactivateHat');
      } else {
        Meteor.call('activateHat');
      }
    }
  });

  var isHatActivated = function () {
    var hat = Devices.findOne({ name: HAT });
    return hat && hat.isActivated;
  };
}
