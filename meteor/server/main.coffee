'use strict'

Meteor.publish 'device', (deviceId) ->
  check deviceId, String
  share.Devices.find deviceId


if share.Devices.find(share.HAT).count() == 0
  share.Devices.insert
    _id: share.HAT
    isActivated: false
    pulseWidth: 0.1

