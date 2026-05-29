class MidiConnectionError(Exception):
    code = "MIDI_DISCONNECTED"

    def __init__(self, message: str = "MIDI device non disponibile.", original: Exception | None = None):
        super().__init__(message)
        self.message = message
        self.original = original
