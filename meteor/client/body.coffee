'use strict'


DEVICE_ID = share.HAT


Template.body.onCreated ->
  @subscribe 'device', DEVICE_ID


Template.body.helpers
  deviceId: DEVICE_ID

  hasDevice: ->
    share.Devices.find(DEVICE_ID).count() != 0

  status: ->
    Meteor.status()

