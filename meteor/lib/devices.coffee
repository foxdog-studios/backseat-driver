'use strict'

share.HAT = 'hat'


share.Devices = new Mongo.Collection 'devices'


Meteor.methods
  setPulseWidth: (deviceId, pulseWidth) ->
    check deviceId, String
    check pulseWidth, Match.Where (x) ->
      check x, Number
      0 <= x <= 1

    numUpdated = share.Devices.update deviceId,
      $set:
        pulseWidth: pulseWidth

    if numUpdated != 1
      throwDeviceUpdateError deviceId

    return

  toggleDevice: (deviceId) ->
    check deviceId, String

    device = share.Devices.findOne
      _id: deviceId
      isActivated:
        $exists: true
    ,
      fields:
        isActivated: 1

    unless device?
      throwDeviceNotFound deviceId

    numUpdated = share.Devices.update deviceId,
      $set:
        isActivated: not device.isActivated

    if numUpdated != 1
      throwDeviceUpdateError deviceId

    return


throwDeviceNotFound = (deviceId) ->
  deviceIdString = JSON.stringify deviceId
  throw new Meteor.Error(
    'device-not-found',
    "Cannot find a sutiable device with the ID #{ deviceIdString }."
  )


throwDeviceUpdateError = (deviceId) ->
  throw new Meteor.Error(
    'device-update-error',
    "Could not update device with the ID #{ JSON.stringify deviceId }."
  )

