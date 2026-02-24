import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class SCPIMixin:
    """Mixin class for SCPI instruments.

    Assumes ``self.adaptor`` is a pyvisa resource and ``self.name`` is available
    (both provided by ScopeDriver). Intended to be used via multiple inheritance
    alongside ScopeDriver.
    """

    # --- Read-only properties (queries) ---

    @property
    def id(self):
        """Instrument identification string (*IDN?)."""
        return self.adaptor.query("*IDN?").strip()

    @property
    def complete(self):
        """Operation complete bit (*OPC?). Returns '1' when all pending operations finish."""
        return self.adaptor.query("*OPC?").strip()

    @property
    def status(self):
        """Status byte and Master Summary Status bit (*STB?)."""
        return self.adaptor.query("*STB?").strip()

    @property
    def options(self):
        """Device options installed (*OPT?)."""
        return self.adaptor.query("*OPT?").strip()

    @property
    def next_error(self):
        """Next error from the error queue (SYST:ERR?).

        Returns:
            tuple: (code: int, message: str)
        """
        response = self.adaptor.query("SYST:ERR?").strip()
        parts = response.split(",", 1)
        code = int(parts[0])
        message = parts[1].strip('"') if len(parts) > 1 else ""
        return code, message

    # --- Command methods ---

    def clear(self):
        """Clear the instrument status byte (*CLS)."""
        self.adaptor.write("*CLS")

    def reset(self):
        """Reset the instrument to factory defaults (*RST)."""
        self.adaptor.write("*RST")

    def check_errors(self):
        """Read and log all errors from the instrument error queue.

        Returns:
            list[tuple]: List of (code, message) tuples for each error found.
        """
        errors = []
        while True:
            code, message = self.next_error
            if code != 0:
                log.error(f"{self.name}: {code}, {message}")
                errors.append((code, message))
            else:
                break
        return errors
