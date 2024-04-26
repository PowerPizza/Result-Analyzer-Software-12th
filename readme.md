## Function of this software
This software is personally build for sort and structuring data of CBSE board examinations result of students. It requires a txt file 
which contain data in a format describe below then this software will sort students, their gender, their roll number and
percentage average etc. Sorted data can be exported as an Excel or JSON file.
    
## Data format
Data should be in a pair of two lines let assume DATA_LINE1 and DATA_LINE2

    DATA_LINE1 :- ROLL_NO GENDER STUDENT_NAME SUB_CODE1 SUB_CODE2 SUB_CODE3......SUB_CODE(n) GRADE1 GRADE2 GRADE3 RESULT COMPARTMENT_SUBJECT_CODES
    DATA_LINE2 :- SUB1_MARKS SUB1_GRADE SUB2_MARKS SUB2_GRADE ...... SUB(n)_MARKS SUB(n)_GRADE
    
### How should be DATA_LINE1 ?
1. ROLL_NO should be in range of 6 to 10 digits.
2. Gender M for male, F for female
3. NAME can contain white spaces.
4. SUB_CODE1 to infinity works just remember that DATA_LINE2 should contain marks and grade of SUB_CODE(n) in proper format.
5. (optional) GRADE1 GRADE2 GRADE3 not actually required software works same if its present of not.
6. RESULT it should be FAIL, PASS, COMP, ABST and its required.

> how should be DATA_LINE2
1. SUB(n)_MARKS and SUB(n)_GRADE represents the marks and grade with respect to SUB_CODE(n).

**Note** : DATA_LINE1 and DATA_LINE2 both are required if any of one missing so software will delete that entry and proceed for next proper paired data lines.

## Configurations/Settings
1. Global Subject Code : Here you can add new subject code and its name in software.


2. Global Max Marks Per Subject : It represents the max marks of which paper held. Like a student got 40 out of 80 so 80
is the max marks. It will be same for all subjects.


3. Global Main Subject : It represents the main subject which is common in all the sides for example english is language
subject which is same for all the fields (science, arts etc.).


4. Global Max Best Subject Range : It represents how many top best subject marks of a student will be consider for
calculate variable columns like average(n), percentage(n) etc. its value should be no_of_best_subjects + 1
for example : 4 + 1 = 5 where no_of_best_subjects = 4 and the 1 here for english/main subject so value of GLOBAL will be 5.


5. Global Dominant Subjects : Its helps to control the column format of table like if we want subject format english
then Physics chemistry .... so we can use this entry to do that. Just provide subject codes and seperate them
using ','.

### [Download for Windows 10 (x64)](https://drive.google.com/drive/folders/1txIDe8C4zpgAWWFcaA6hIGqVmqLnF5XQ?usp=sharing)