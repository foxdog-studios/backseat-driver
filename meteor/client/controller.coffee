'use strict'

Template.Controller.onCreated ->
  check @data, deviceId: String
  @subscribe 'device', @data.deviceId


Template.Controller.helpers
  buttonClass: ->
    if isDeviceActivated this
      'active'

  buttonSuffix: ->
    if isDeviceActivated(this) then 'on' else 'off'

  hasDevice: ->
    share.Devices.find(@deviceId).count() != 0

  status: ->
    Meteor.status()


Template.Controller.events
  'click #party-hat': (event, template) ->
    event.preventDefault()
    event.target.disabled = true
    Meteor.call 'toggleDevice', template.data.deviceId, (error, result) ->
      event.target.disabled = false
      console.log error if error?

  'input #pulse-width': (event, template) ->
    deviceId = template.data.deviceId
    pulseWidth = parseFloat event.target.value
    Meteor.call 'setPulseWidth', deviceId, pulseWidth


isDeviceActivated = (data) ->
  share.Devices.findOne(data.deviceId).isActivated

