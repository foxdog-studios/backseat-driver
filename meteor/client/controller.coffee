'use strict'

Template.Controller.onCreated ->
  check @data, deviceId: String


Template.Controller.onRendered ->
  @_controller = new Controller @data.deviceId
  @_controller.enable @find 'canvas'


Template.Controller.onDestroyed ->
  @_controller.disable()
  @_controller = null


class Controller
  constructor: (@_deviceId) ->
    @_$canvas = null
    @_canvas = null
    @_computation = null
    @_ctx = null
    @_isEnabled = false
    @_isMouseDown = false
    @_touchId = null

    if window.navigator.msPointerEnabled
      @_mouseDownName = 'pointerdown'
      @_mouseMoveName = 'pointermove'
      @_mouseUpName = 'pointerup'
    else
      @_mouseDownName = 'mousedown'
      @_mouseMoveName = 'mousemove'
      @_mouseUpName = 'mouseup'

  enable: (canvas) ->
    if @_isEnabled
      throw new Error 'Controller is already enabled'
    @_isEnabled = true
    @_canvas = canvas
    @_$canvas = $(@_canvas)
    @_ctx = @_canvas.getContext '2d'
    @_withStaticHandlers 'on'
    @_resize()
    @_computation = Tracker.autorun @_onDeviceChange
    return

  disable: ->
    unless @_isEnabled
      throw new Error 'Controller is already disabled'
    @_computation.stop()
    @_computation = null
    @_withMouseMoveHandler 'off'
    @_withStaticHandlers 'off'
    @_touchId = null
    @_isMouseDown = false
    @_ctx = null
    @_$canvas = null
    @_canvas = null
    @_isEnabled = false
    return

  _withStaticHandlers: (action) ->
    @_withHandlers @_$canvas, action, [
      [@_mouseDownName, @_onMouseDown ]
      [@_mouseUpName  , @_onMouseUp   ]
      ['touchstart'   , @_onTouchStart]
      ['touchmove'    , @_onTouchMove ]
      ['touchend'     , @_onTouchEnd  ]
    ]

    @_withHandlers $(window), action, [['resize', @_onResize]]
    return

  _withMouseMoveHandler: (action) ->
    @_withHandlers @_$canvas, action, [[@_mouseMoveName, @_onMouseMove]]
    return

  _withHandlers: (target, action, handlers) ->
    for [eventName, handler] in handlers
      target[action] eventName, handler
    return

  _onResize: (event) =>
    @_resize()
    @_draw()
    return

  _onMouseDown: (event) =>
    event.preventDefault()
    @_withMouseMoveHandler 'on'
    @_setDeviceActive event.pageY
    return

  _onMouseMove: (event) =>
    event.preventDefault()
    @_setPulseWidth event.pageY
    return

  _onMouseUp: (event) =>
    event.preventDefault()
    @_setDeviceInactive()
    @_withMouseMoveHandler 'off'
    return

  _onTouchStart: (event) =>
    event.preventDefault()
    unless @_touchId?
      touch = event.originalEvent.changedTouches[0]
      @_touchId = touch.identifier
      @_setDeviceActive touch.pageY
    return

  _onTouchMove: (event) =>
    event.preventDefault()
    for touch in event.originalEvent.changedTouches
      if touch.identifier == @_touchId
        @_setPulseWidth touch.pageY
        break
    return

  _onTouchEnd: (event) =>
    event.preventDefault()
    for touch in event.originalEvent.changedTouches
      if touch.identifier == @_touchId
        @_touchId = null
        @_setDeviceInactive()
        break
    return

  _setDeviceActive: (pageY) ->
    Meteor.call 'setDeviceActive', @_deviceId, @_calcPulseWidth pageY
    return

  _setPulseWidth: (pageY) ->
    Meteor.call 'setPulseWidth', @_deviceId,  @_calcPulseWidth pageY
    return

  _calcPulseWidth: (pageY) ->
    {top} = @_$canvas.offset()
    pulseWidth = 1 - ((pageY - top) / @_$canvas.height())
    if pulseWidth < 0
      pulseWidth = 0
    else if pulseWidth > 1
      pulseWidth = 1
    pulseWidth

  _setDeviceInactive: ->
    Meteor.call 'setDeviceInactive', @_deviceId
    return

  _onDeviceChange: =>
    @_clear()
    device = share.Devices.findOne @_deviceId,
      fields:
        isActivated: 1
    @_draw device if device?
    return

  _resize: ->
    $window = $(window)
    @_canvas.width = $window.width()
    @_canvas.height = $window.height()
    return

  _clear: ->
    @_ctx.clearRect 0, 0, @_canvas.width, @_canvas.height
    return

  _draw: (device) ->
    @_ctx.fillStyle = if device.isActivated
      'GreenYellow'
    else
      'White'
    @_ctx.fillRect 0, 0, @_canvas.width, @_canvas.height

    x = Math.round @_canvas.width / 2
    y = Math.round @_canvas.height / 2
    state = if device.isActivated then 'ON' else 'OFF'
    @_ctx.fillStyle = 'Black'
    @_ctx.font = '150px serf'
    @_ctx.textAlign = 'center'
    @_ctx.textBaseline = 'middle'
    @_ctx.fillText "Party is #{ state }", x, y

    return

