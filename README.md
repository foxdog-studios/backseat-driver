Backseat Driver
===============

Crowd controlled car


Setup
-----

If you're using a Linux based or OSX system, follow the instructions below. If
you're using a Window system, install [Ubuntu](http://www.ubuntu.com/desktop),
then follow the instructions below. If you're using another system, try the
instructions below and let me know how it goes.

1.  Ensure you have the following programs installed using your system's package
    manager (preferred) or by retrieving them from the Web.

    * A POSIX compliant shell, e.g., bash (you almost certainly have one
      already).

    * [Git](http://git-scm.com/downloads)

    * [Python 2.7](https://www.python.org/download/releases/2.7.6/)

    * [cURL](http://curl.haxx.se/download.html) (you probably already have
      this).

    * [virtualenv](http://www.virtualenv.org/en/latest/) for Python 2.7


2.  Clone the Backseat Driver repository.

    ```shell
    $ git clone https://github.com/foxdog-studios/backseat-driver.git
    ```

3.  Change your working directory to be the repository.

    ```shell
    $ cd backseat-driver
    ```

5.  Run the setup script. This will install Meteor and Meteorite, create a
    Python 2.7 virtual environment and install the required Python packages.
    *You may be prompted for your password by `sudo`.*

    ```shell
    $ ./setup.sh
    ```

Running
-------

1. To launch the Meteor site, run;

    ```shell
    $ cd meteor
    $ mrt
    ```

    from the root of the repository.

2. Connect a Arduino board to your system and find it's device path. On my
   system, this can be done with;

   ```shell
   $ ls /dev/ttyACM*
   /dev/ttyACM0
   ```

3. To launch the hat controller, run;

    ```shell
    $ . venv/bin/activate
    $ python hat_controller $DEVICE_PATH
    ```

    from the root of the repository. Replace `$DEVICE_PATH` with the path you
    found in step 2.

4. Finally, launch a browser and navigate to `http://localhost:3000`.

