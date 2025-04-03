# Analysis

## Layer 1, Head 2

This attention head in the first layer demonstrates a predominantly local focus. It assigns higher weights to tokens immediately adjacent to each word, capturing basic syntactic structures such as short-range dependencies and function word relationships. This behavior helps the model establish the foundation of the sentence's structure, which is typical for early layers where low-level features (e.g., parts of speech and local context) are learned.

Example Sentences:
- "i had a country walk on thursday and came home in a dreadful mess"
- "she smiled and i sat"

## Layer 12, Head 8

In contrast, this head in the final layer exhibits a broader, more global attention pattern. It tends to focus on semantically important words across longer distances, such as key nouns and verbs, and often gives special attention to the masked token to support accurate predictions. This pattern is indicative of higher-level abstraction, where the model integrates global context and long-distance dependencies to understand the overall meaning of the sentence.

Example Sentences:
- "my companion arrived and said a word"
- "he lit the pipe before leaving home"
