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

### 🔄 Dynamic Configuration

ConvoLingo passes variables to the VAPI assistant:
- `native_language`: The language you speak (default: English)
- `target_language`: The language you want to learn (default: German)
- `chapter`: The learning module or topic (default: "Chapter 3: Ordering a donner")

**Important Note**: When using the default chapter, ConvoLingo uses a pre-configured assistant on the VAPI platform. When you specify a custom chapter using the `--chapter` parameter, ConvoLingo creates a new custom assistant on-the-fly with your specified chapter embedded directly in the system prompt.

To change languages or chapter, use the command-line options:
```
convolingo session --target Spanish --origin English --chapter "Chapter 1: Restaurant Basics"
```

#### How Chapter Selection Works

ConvoLingo now supports custom chapters in two ways:

1. **Default Chapter**: Uses the pre-configured assistant (which has "Chapter 3: Ordering a donner" built in)
2. **Custom Chapter**: Creates a custom assistant with your specified chapter text

This approach ensures that specifying a different chapter actually changes the conversation topic, even if the default assistant's system prompt has a hardcoded chapter.

#### Example Commands

For default chapter:
```
convolingo session --target German --origin English
```

For custom chapter:
```
convolingo session --target Spanish --origin English --chapter "Chapter 1: Restaurant Basics (ordering drinks, asking for menu)"
```

#### Troubleshooting Variable Usage

If certain variables don't seem to affect the conversation:

1. For the `chapter` parameter, make sure you're using a value different from the default
2. Verify that the logs show "Created custom assistant with chapter: [your chapter]"
3. For language variables, check that they're being recognized in the assistant's responses

Multiple variable names for the same content are passed by default to maximize compatibility with different Vapi assistant configurations.

## 🐞 Problems?

- Make sure your magic key in `.env` is right!
- Try reinstalling: `pip install -e .`
- Make sure you're in the right folder when typing commands

## 📜 License

MIT - That means it's free to use and share! 