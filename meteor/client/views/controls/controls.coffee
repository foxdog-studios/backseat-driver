Template.controller.helpers
  buttonSuffix: ->
    if isHatActivated() then 'off' else 'on'

Template.controller.events
  'click #led': (event) ->
    event.preventDefault()
    if isHatActivated()
      Meteor.call 'deactivateHat'
    else
      Meteor.call 'activateHat'

isHatActivated = ->
  hat = Devices.findOne name: HAT
  hat?.isActivated

