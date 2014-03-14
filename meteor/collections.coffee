@HAT = 'hat'

@Devices = new Meteor.Collection 'devices'

Meteor.methods
  'activateHat'  : -> setHatState true
  'deactivateHat': -> setHatState false

setHatState = (isActivated) ->
  Devices.upsert
    name: HAT
  ,
    name: HAT
    isActivated: isActivated
  return

if Meteor.isServer
  Meteor.publish 'hat', ->
    Devices.find name: HAT
else
  Meteor.subscribe 'hat'

