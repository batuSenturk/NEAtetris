# Documentation for `clear_lines` and `remove_lines` Methods

## `clear_lines` Method

### Purpose
The `clear_lines` method is responsible for identifying and marking the lines in the grid that are completely filled with blocks. Once identified, it triggers the removal of these lines.

### Functionality
1. **Initialization**: 
   - It starts by resetting the `lines_to_clear` list to an empty state. This ensures that any previous line markings are cleared before checking for new filled lines.

2. **Line Checking**:
   - The method iterates over the grid from the bottom row to the top (using a reverse loop). This is important because when lines are removed, it prevents the shifting of rows from affecting the checking of lines above.
   - For each row, it checks if all cells in that row are filled (i.e., not equal to 0). This is done using the `all()` function, which returns `True` only if all conditions are met.

3. **Marking Lines**:
   - If a row is found to be completely filled, its index is appended to the `lines_to_clear` list.

4. **Removing Lines**:
   - If any lines are marked for clearing, the method calls `remove_lines()` to handle the actual removal process.

5. **Return Value**:
   - Finally, the method returns the count of lines that were marked for clearing, which can be useful for scoring or feedback purposes.

### Example Usage


---

## `remove_lines` Method

### Purpose
The `remove_lines` method is responsible for removing the lines that have been marked for clearing from the grid and shifting the remaining lines down.

### Functionality
1. **New Cells Initialization**:
   - It creates a new list of cells (`new_cells`) that will represent the cleared lines. The number of rows in `new_cells` is equal to the number of lines that were marked for clearing (`self.lines_to_clear`), and all cells in this new list are initialized to 0 (indicating empty).

2. **Old Cells Filtering**:
   - The method constructs a list of the remaining rows (`old_cells`) by filtering out the rows that were marked for clearing. This is done using a list comprehension that includes only those rows whose indices are not in `self.lines_to_clear`.

3. **Updating the Grid**:
   - The grid's `cells` attribute is updated to be a combination of the new empty rows (`new_cells`) followed by the remaining old rows (`old_cells`). This effectively removes the filled lines and shifts the remaining lines down.

4. **Resetting Lines to Clear**:
   - After the removal process, the `lines_to_clear` list is reset to an empty state to prepare for the next clearing operation.

### Example Usage


---

### Summary
- The `clear_lines` method identifies filled lines in the grid and marks them for removal, while the `remove_lines` method executes the actual removal and shifting of the grid's rows. Together, they manage the dynamic nature of the grid in response to gameplay events, such as clearing lines in a Tetris-like game.