# Tutorial

How to stick together the web and hardware. It goes over how to create a very
basic meteor application and then allows you to connect it to an Arduino device.

## Install meteor

Open a terminal and enter

    curl https://install.meteor.com/ | sh


## Create a meteor app

We will name our app `hat`

    meteor create hat


## Run your app

    cd hat
    meteor


Open a browser and go to http://localhost:3000/


## In a text editor open hat.js

    if (Meteor.isClient) {
      Template.hello.greeting = function () {
        return "Welcome to hat.";
      };

      Template.hello.events({
        'click input': function () {
          // template data, if any, is available in 'this'
          if (typeof console !== 'undefined')
            console.log("You pressed the button");
        }
      });
    }

    if (Meteor.isServer) {
      Meteor.startup(function () {
        // code to run on server at startup
      });
    }

We'll start on a clean slate so delete the contents of the file and replace them
with this.

    if (Meteor.isClient) {
      console.log('I am on the client only');
    }
    if (Meteor.isServer) {
      console.log('I am on the server only');
    }

    console.log('I am on both client and server');

If you are still running the server it should automatically restart when you
make changes to the file and the browser should automatically reload too.

Look at the output from the server and open up the console in the browser
(press `F12`) and look its output. You'll see that some code ran differently
depending on where it was (client/server) but there was also code shared between
the server and the client.

## HTML Templates

In an editor open `hat.html`

    <head>
      <title>hat</title>
    </head>

    <body>
      {{> hello}}
    </body>

    <template name="hello">
      <h1>Hello World!</h1>
      {{greeting}}
      <input type="button" value="Click" />
    </template>

Lets edit it so that we just have a button

    <head>
      <title>Party hat</title>
    </head>

    <body>
      {{> controller}}
    </body>

    <template name="controller">
      <button id="party-hat">Party is {{buttonSuffix}}</button>
    </template>

Now edit `hat.js` and add a template helper

    if (Meteor.isClient) {
      console.log('I am on the client only');

      Template.controller.helpers({
        buttonSuffix: function () {
          return 'off';
        }
      });
    }
    if (Meteor.isServer) {
      console.log('I am on the server only');
    }

    console.log('I am on both client and server');

Now you should see a button that says the party is off in the browser.

We should change that.


## Collections

Meteor has a mongodb built in to it, no need to install. It is available on the
client too (as minimongo, a mini stripped-down version of mongo).

    HAT = 'hat';

    Devices = new Meteor.Collection('devices');

    if (Meteor.isServer) {
      if (Devices.find().count() === 0) {
        Devices.insert({
          _id: HAT,
          isActivated: false
        });
      }
    }

    if (Meteor.isClient) {
      Template.controller.helpers({
        buttonSuffix: function () {
          return 'off';
        }
      });
    }

We've removed the `console.log`s to get a cleaner view and have moved the server
only stuff above the client.

Importantly, we have created a collection called `Devices`. This is on both
client and server and will allow for data to be synchronised between both.

We also bootstrap this with a device.

## Changing data

When the button is pressed we can update the collection

    HAT = 'hat';

    Devices = new Meteor.Collection('devices');

    if (Meteor.isServer) {
      if (Devices.find().count() === 0) {
        Devices.insert({
          _id: HAT,
          isActivated: false
        });
      }
    }

    if (Meteor.isClient) {

      var setHatState = function (isActivated) {
        Devices.update(HAT, {
          isActivated: isActivated
        });
      };

      var isHatActivated = function () {
        var hat = Devices.findOne(HAT);
        return hat && hat.isActivated;
      };

      Template.controller.helpers({
        buttonSuffix: function () {
          return isHatActivated() ? 'on' : 'off';
        }
      });

      Template.controller.events({
        'click #party-hat': function (event) {
          event.preventDefault();
          setHatState(!isHatActivated());
        }
      });
    }

If that works you can now see that the party can be off, or the party can be on.

Open another browser window and watch them all update automatically.


## Talking the server from outside the browser

Meteor does all of its communication via a messaging protocol called DDP.

If we write a client (in any language) that can communicate in DDP, then it easy
to communicate with the meteor server.

We have written a small python DDP library. This allows us to use python to
communicate with the meteor server, meaning we can easily talk to hardware such
as Arduinos.

For this we can use a command line utility we have written with the library.

Follow the instructions in the `README` to run it.


