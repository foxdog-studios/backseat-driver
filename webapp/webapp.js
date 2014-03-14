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
    active: function () {
      return isHatActivated() ? 'active' : null;
    },
    buttonSuffix: function () {
      return isHatActivated() ? 'on' : 'off';
    }
  });

  Template.controller.events({
    'click #party-hat': function (event) {
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
