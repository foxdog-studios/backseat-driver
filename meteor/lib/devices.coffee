'use strict'

share.HAT = 'hat'


share.Devices = new Mongo.Collection 'devices'


Meteor.methods
  setDeviceActive: (deviceId, pulseWidth) ->
    check deviceId, String
    check pulseWidth, MatchPulseWidth
    numUpdated = share.Devices.update
      _id: deviceId
    ,
      $set:
        isActivated: true
        pulseWidth: pulseWidth
    if numUpdated != 1
      throwDeviceUpdateError deviceId
    return


  setDeviceInactive: (deviceId) ->
    check deviceId, String
    numUpdated = share.Devices.update
      _id: deviceId
    ,
      $set:
        isActivated: false
    if numUpdated != 1
      throwDeviceUpdateError deviceId
    return


  setPulseWidth: (deviceId, pulseWidth) ->
    check deviceId, String
    check pulseWidth, MatchPulseWidth
    numUpdated = share.Devices.update deviceId,
      $set:
        pulseWidth: pulseWidth
    if numUpdated != 1
      throwDeviceUpdateError deviceId
    return


throwDeviceUpdateError = (deviceId) ->
  throw new Meteor.Error(
    'device-update-error',
    "Could not update device with the ID #{ JSON.stringify deviceId }."
  )


MatchPulseWidth = Match.Where (x) ->
  check x, Number
  0 <= x <= 1

