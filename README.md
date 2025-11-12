# Antidote  
<img src="src/bsrc/docs/antidote.png" alt="Antidote Logo" width="300">

**Antidote** is an experimental encryption algorithm with a minimal UI for sending messages — locally, securely, and without oversight.


## Why should we care?

Because we don’t.  
Sell drugs, talk about aliens, or plan your next Fortnite match, whatever.  
Antidote makes sure no one else sees that message.  

This isn’t another messaging app.  
This is a **protest** against forced identification and chat surveillance.  
No sign-ins. No phone numbers. No cloud. Just math and silicone.


## What it does (for now)

- Generates **public/private keypairs** using a custom elliptic curve system.  
- Encrypts and signs messages locally.  
- Decrypts messages using receiver keys.  
- Keeps everything **offline** and **local**, meaning no external servers.  

At this point, it’s more like **PGP with attitude** than a finished messenger.


## In progress

- Implementing full message authentication and signature verification.  
- Integrating a local message UI.  
- Experimenting with **Tor routing** for peer-to-peer communication.  
- Planning compression + QR encoding for message transfer.


## Structure (rough)

```
antidote/
├── src/
│ ├── core/ # encryption logic
│ ├── network/ # Tor network placeholder
│ ├── ui/ # user interface
│ ├── bsrc/docs/ # images + markdown stuff
│ └── tests/ # early testing scripts
├── README.md
├── LICENCE
├── .gitignore
└── requierments.txt

```

## Status

Work in progress, currently prototyping the algorithm’s **core logic** before UI + network integration.  
If you’re reading this, you’re early. Like, pre-alpha early.


## Future vision

A local-first, Tor-connected messaging app that nobody controls, and nobody can trace.  
Not another social platform. just **encrypted freedom**.

## Disclaimer

This project is **for educational and privacy research** purposes.  
Not intended for illegal use. You break it, you buy it.


### Made with a dream and caffeine, please open issues with my code