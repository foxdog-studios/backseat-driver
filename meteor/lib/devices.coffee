'use strict'

share.HAT = 'hat'


share.Devices = new Mongo.Collection 'devices'


Meteor.methods
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
      deviceIdString = JSON.stringify deviceId
      throw new Meteor.Error(
        'device-not-found',
        "Cannot find a sutiable device with the ID #{ deviceIdString }."
      )

    numUpdated = share.Devices.update deviceId,
      $set:
        isActivated: not device.isActivated

    if numUpdated != 1
      throw new Meteor.Error(
        'device-toggle-error',
        "Could not toggle device with the ID #{ JSON.stringify deviceId }."
      )

    return

