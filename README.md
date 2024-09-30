# Missing Vowels

## Play
Play the missing vowels round from Only Connect!
<br>
You will be given only consonants from well known phrases and words from the given categoery with the vowels removed. You need to guess what the full word is and type it in. For example, if the question is "NGLND" and the category is Countries, the answer would be "ENGLAND".<br>
Try it out and challenge yourself. WWhat's the longest streak you can get?
<br>
Run `./missingvowels` 
or 
`missingvowels` if it has been added to your $PATH

## Files
| Filename | Description| 
| ---------| -----------|
| missingvowels | The main script to run. Can be added to path |
| data/db_* | All files to be used as questions should be saved as data/db_[name]. No file extension required. The name of the file will be considered as the category name |
| data/questionsets.p | Pickle file that is created that contains the questions created from the db_[name] files |
| data/.highscore | The file that locally scores the highest winning streak |

## Adding new datasets
Add a file named `db_[name]` where `name` is a category of the files. Do not include whitespaces in the `name`, instead use '-' as the separator.
Ensure there is only one entry per line of the file.
