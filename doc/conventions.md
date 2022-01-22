# Modding conventions

Used by lfgr for MNAI and EMM modding.

These conventions are often only apply to newly added code. I think large refactorings are usually worth it, but if there were no real conventions in place beforehand (e.g., text file names), it doesn't hurt to proceed in a more structural way.

## Text

Do not add translations that are identical to the English phrase.

### File names

`InfoName.xml` (e.g., `Votes.xml`): Text for specific info objects, e.g., description or help.

`InfoNameHelp.xml` (e.g., `VotesHelp.xml`): Generic text related to the info type, e.g., auto-generated help text.

## C++

Use Hungarian notation like in the original code.

Use the following parenthesis style for functions, loops, conditionals, etc. (like in the original code):
```C++
void f()
{
    ...
}
```