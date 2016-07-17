# techtest-wordladder
Given two words (start and end) and the dictionary, find the length of the shortest transformation sequence

from start to end, such that:

> Only one letter can be changed at a time

> Each intermediate word must exist in the given dictionary

For example:
```python
start = “hit”

end = “cog”

dictionary = [“hot”,”dot”,”dog”,”lot”,”log”]
```
As one of the shortest transformations is "hit" -> "hot" -> "dot" -> "dog" -> "cog", return its length 4.

Note: All words have the same length. All words contain only lowercase alphabetic characters.
