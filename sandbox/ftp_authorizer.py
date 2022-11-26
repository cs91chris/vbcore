# type: ignore
import os
import warnings

from pyftpdlib.authorizers import AuthenticationFailed

unicode = str


class UserRepo(object):
    def __init__(self):
        self.user_table = {}

    def add(
        self,
        username,
        password,
        homedir,
        perm="elr",
        msg_login="Login successful.",
        msg_quit="Goodbye.",
        operms=None,
    ):
        dic = {
            "pwd": str(password),
            "home": homedir,
            "perm": perm,
            "operms": operms or {},
            "msg_login": str(msg_login),
            "msg_quit": str(msg_quit),
        }
        self.user_table[username] = dic

    def get(self, username):
        return self.user_table.get(username)

    def remove(self, username):
        del self.user_table[username]

    def override_perm(self, username, directory, perm, recursive):
        self.user_table[username]["operms"][directory] = perm, recursive


class Authorizer(object):
    read_perms = "elr"
    write_perms = "adfmwMT"

    def __init__(self, repo: UserRepo):
        self.repo = repo

    def add_user(
        self,
        username,
        password,
        homedir,
        perm="elr",
        msg_login="Login successful.",
        msg_quit="Goodbye.",
    ):
        """Add a user to the virtual users table.

        AuthorizerError exceptions raised on error conditions such as
        invalid permissions, missing home directory or duplicate usernames.

        Optional perm argument is a string referencing the user's
        permissions explained below:

        Read permissions:
         - "e" = change directory (CWD command)
         - "l" = list files (LIST, NLST, STAT, MLSD, MLST, SIZE, MDTM commands)
         - "r" = retrieve file from the server (RETR command)

        Write permissions:
         - "a" = append data to an existing file (APPE command)
         - "d" = delete file or directory (DELE, RMD commands)
         - "f" = rename file or directory (RNFR, RNTO commands)
         - "m" = create directory (MKD command)
         - "w" = store a file to the server (STOR, STOU commands)
         - "M" = change file mode (SITE CHMOD command)
         - "T" = update file last modified time (MFMT command)

        Optional msg_login and msg_quit arguments can be specified to
        provide customized response strings when user log-in and quit.
        """
        if self.has_user(username):
            raise ValueError("user %r already exists" % username)
        if not isinstance(homedir, unicode):
            homedir = homedir.decode("utf8")
        if not os.path.isdir(homedir):
            raise ValueError("no such directory: %r" % homedir)
        homedir = os.path.realpath(homedir)
        self._check_permissions(username, perm)
        self.repo.add(username, password, homedir, perm, str(msg_login), str(msg_quit))

    def add_anonymous(self, homedir, **kwargs):
        """Add an anonymous user to the virtual users table.

        AuthorizerError exception raised on error conditions such as
        invalid permissions, missing home directory, or duplicate
        anonymous users.

        The keyword arguments in kwargs are the same expected by
        add_user method: "perm", "msg_login" and "msg_quit".

        The optional "perm" keyword argument is a string defaulting to
        "elr" referencing "read-only" anonymous user's permissions.

        Using write permission values ("adfmwM") results in a
        RuntimeWarning.
        """
        self.add_user(self, "anonymous", "", homedir, **kwargs)

    def remove_user(self, username):
        """Remove a user from the virtual users table."""
        self.repo.remove(username)

    def override_perm(self, username, directory, perm, recursive=False):
        """Override permissions for a given directory."""
        self._check_permissions(username, perm)
        if not os.path.isdir(directory):
            raise ValueError("no such directory: %r" % directory)
        directory = os.path.normcase(os.path.realpath(directory))
        home = os.path.normcase(self.get_home_dir(username))
        if directory == home:
            raise ValueError("can't override home directory permissions")
        if not self._issubpath(directory, home):
            raise ValueError("path escapes user home directory")
        self.repo.override_perm(username, directory, perm, recursive)

    def validate_authentication(self, username, password, handler):
        """Raises AuthenticationFailed if supplied username and
        password don't match the stored credentials, else return
        None.
        """
        msg = "Authentication failed."
        if not self.has_user(username):
            if username == "anonymous":
                msg = "Anonymous access not allowed."
            raise AuthenticationFailed(msg)
        if username != "anonymous":
            if self.repo.get(username)["pwd"] != password:
                raise AuthenticationFailed(msg)

    def get_home_dir(self, username):
        """Return the user's home directory.
        Since this is called during authentication (PASS),
        AuthenticationFailed can be freely raised by subclasses in case
        the provided username no longer exists.
        """
        return self.repo.get(username)["home"]

    def impersonate_user(self, username, password):
        """Impersonate another user (noop).

        It is always called before accessing the filesystem.
        By default it does nothing.  The subclass overriding this
        method is expected to provide a mechanism to change the
        current user.
        """

    def terminate_impersonation(self, username):
        """Terminate impersonation (noop).

        It is always called after having accessed the filesystem.
        By default it does nothing.  The subclass overriding this
        method is expected to provide a mechanism to switch back
        to the original user.
        """

    def has_user(self, username):
        """Whether the username exists in the virtual users table."""
        return self.repo.get(username) is not None

    def has_perm(self, username, perm, path=None):
        """Whether the user has permission over path (an absolute
        pathname of a file or a directory).

        Expected perm argument is one of the following letters:
        "elradfmwMT".
        """
        if path is None:
            return perm in self.repo.get(username)["perm"]

        path = os.path.normcase(path)
        for dir in self.repo.get(username)["operms"].keys():
            operm, recursive = self.repo.get(username)["operms"][dir]
            if self._issubpath(path, dir):
                if recursive:
                    return perm in operm
                if (
                    path == dir
                    or os.path.dirname(path) == dir
                    and not os.path.isdir(path)
                ):
                    return perm in operm

        return perm in self.repo.get(username)["perm"]

    def get_perms(self, username):
        """Return current user permissions."""
        return self.repo.get(username)["perm"]

    def get_msg_login(self, username):
        """Return the user's login message."""
        return self.repo.get(username)["msg_login"]

    def get_msg_quit(self, username):
        """Return the user's quitting message."""
        try:
            return self.repo.get(username)["msg_quit"]
        except KeyError:
            return "Goodbye."

    def _check_permissions(self, username, perm):
        warned = 0
        for p in perm:
            if p not in self.read_perms + self.write_perms:
                raise ValueError("no such permission %r" % p)
            if username == "anonymous" and p in self.write_perms and not warned:
                warnings.warn(
                    "write permissions assigned to anonymous user.", RuntimeWarning
                )
                warned = 1

    def _issubpath(self, a, b):
        """Return True if a is a sub-path of b or if the paths are equal."""
        p1 = a.rstrip(os.sep).split(os.sep)
        p2 = b.rstrip(os.sep).split(os.sep)
        return p1[: len(p2)] == p2
