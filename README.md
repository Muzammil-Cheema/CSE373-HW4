# Homework 4: Set Cover

## How To Run
After downloading any required packages (pip install requirements.txt), run the main.py file. All test files are 
already downloaded in the 
"/Data" directory. Running the main.py file will test all files consecutively. 

## Notable Optimizations
<ul>
    <li> Exclude empty sets from the initial subset building during file parsing (empty sets will never contribute to the solution). </li>
    <li> Exclude proper subsets of the given sets in the initial subset building during file parsing (proper subsets provide no extra value). </li>
    <li> Use bitmasks to represent sets for faster union operations and solution checking. </li>
</ul>

