# voice-out-translator

Captures and translates/transcribes computer audio output in real-time.

## Using the program

The help command is `voice-out-translator --help`. This command returns:

```bash
usage: voice-out-translator [-h] [--source-type {output,input}] [--device-name DEVICE_NAME] [--autostart] [--applications]

Voice Out Translator - Translate and transcribe audio output/input

```

Options:

```bash

  -h, --help            show this help message and exit
  --source-type {output,input}
                        Type of audio source to monitor (default: output)
  --device-name DEVICE_NAME
                        Name of virtual device (default: VirtualOutput for output, VirtualInput for input)
  --autostart           Install autostart desktop file and exit
  --applications        Install application menu entry and exit

```

Examples:

```bash
# Run with default settings (output monitoring)
voice-out-translator

# Explicitly monitor audio output
voice-out-translator --source-type output --device-name VirtualOutput

# Monitor audio input (microphone)  
voice-out-translator --source-type input --device-name VirtualInput

# Install autostart desktop file
voice-out-translator --autostart

# Install application menu entry
voice-out-translator --applications

```

