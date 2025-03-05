# ConvoLingo - Talk and Learn New Languages! 🗣️🌍

ConvoLingo is a fun app that helps you learn new languages by talking with an AI teacher!

## 🚀 Quick Start

1. Make sure you have Python installed on your computer.

2. Put your magic key in a file called `.env`:
   ```
   VAPI_API_KEY=your_magic_key_here
   ```

3. Install ConvoLingo:
   ```
   cd convo-lingo
   pip install -e .
   ```

4. Start talking in your new language:
   ```
   convolingo interactive --target German
   ```

## 🎮 Fun Commands

### Talk and Learn
```
convolingo interactive --target German --origin English
```
This starts a fun chat where you can practice German! Type messages and get replies.

### Set Up Special Tools
```
convolingo setup
```
This sets up special tools like a vocabulary helper!

## 📝 What You Can Learn

You can learn many languages:
- German 🇩🇪
- More TBA

## 🛠️ For Grown-Ups

ConvoLingo is organized like this:

```
convo-lingo/              # Main folder
├── README.md             # This guide
├── setup.py              # Installation settings
├── .env                  # Your magic key goes here!
├── convolingo/           # App code
    ├── __main__.py       # Starting point
    ├── api/              # Talking to the teacher
    ├── cli/              # Command buttons
    ├── tools/            # Helper tools
    └── utils/            # Useful extras
```

## 🐞 Problems?

- Make sure your magic key in `.env` is right!
- Try reinstalling: `pip install -e .`
- Make sure you're in the right folder when typing commands

## 📜 License

MIT - That means it's free to use and share! 