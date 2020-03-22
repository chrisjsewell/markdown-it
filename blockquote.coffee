# Block quotes
'use strict'
isSpace = require('../common/utils').isSpace

module.exports = (state, startLine, endLine, silent) ->
  adjustTab = undefined
  ch = undefined
  i = undefined
  initial = undefined
  l = undefined
  lastLineEmpty = undefined
  lines = undefined
  nextLine = undefined
  offset = undefined
  oldBMarks = undefined
  oldBSCount = undefined
  oldIndent = undefined
  oldParentType = undefined
  oldSCount = undefined
  oldTShift = undefined
  spaceAfterMarker = undefined
  terminate = undefined
  terminatorRules = undefined
  token = undefined
  wasOutdented = undefined
  oldLineMax = state.lineMax
  pos = state.bMarks[startLine] + state.tShift[startLine]
  max = state.eMarks[startLine]
  # if it's indented more than 3 spaces, it should be a code block
  if state.sCount[startLine] - (state.blkIndent) >= 4
    return false
  # check the block quote marker
  if state.src.charCodeAt(pos++) != 0x3E
    return false
  # we know that it's going to be a valid blockquote,
  # so no point trying to find the end of it in silent mode
  if silent
    return true
  # skip spaces after ">" and re-calculate offset
  initial = offset = state.sCount[startLine] + pos - (state.bMarks[startLine] + state.tShift[startLine])
  # skip one optional space after '>'
  if state.src.charCodeAt(pos) == 0x20
    # ' >   test '
    #     ^ -- position start of line here:
    pos++
    initial++
    offset++
    adjustTab = false
    spaceAfterMarker = true
  else if state.src.charCodeAt(pos) == 0x09
    spaceAfterMarker = true
    if (state.bsCount[startLine] + offset) % 4 == 3
      # '  >\t  test '
      #       ^ -- position start of line here (tab has width===1)
      pos++
      initial++
      offset++
      adjustTab = false
    else
      # ' >\t  test '
      #    ^ -- position start of line here + shift bsCount slightly
      #         to make extra space appear
      adjustTab = true
  else
    spaceAfterMarker = false
  oldBMarks = [ state.bMarks[startLine] ]
  state.bMarks[startLine] = pos
  while pos < max
    ch = state.src.charCodeAt(pos)
    if isSpace(ch)
      if ch == 0x09
        offset += 4 - ((offset + state.bsCount[startLine] + (if adjustTab then 1 else 0)) % 4)
      else
        offset++
    else
      break
    pos++
  oldBSCount = [ state.bsCount[startLine] ]
  state.bsCount[startLine] = state.sCount[startLine] + 1 + (if spaceAfterMarker then 1 else 0)
  lastLineEmpty = pos >= max
  oldSCount = [ state.sCount[startLine] ]
  state.sCount[startLine] = offset - initial
  oldTShift = [ state.tShift[startLine] ]
  state.tShift[startLine] = pos - (state.bMarks[startLine])
  terminatorRules = state.md.block.ruler.getRules('blockquote')
  oldParentType = state.parentType
  state.parentType = 'blockquote'
  wasOutdented = false
  # Search the end of the block
  #
  # Block ends with either:
  #  1. an empty line outside:
  #     ```
  #     > test
  #
  #     ```
  #  2. an empty line inside:
  #     ```
  #     >
  #     test
  #     ```
  #  3. another tag:
  #     ```
  #     > test
  #      - - -
  #     ```
  nextLine = startLine + 1
  while nextLine < endLine
    # check if it's outdented, i.e. it's inside list item and indented
    # less than said list item:
    #
    # ```
    # 1. anything
    #    > current blockquote
    # 2. checking this line
    # ```
    if state.sCount[nextLine] < state.blkIndent
      wasOutdented = true
    pos = state.bMarks[nextLine] + state.tShift[nextLine]
    max = state.eMarks[nextLine]
    if pos >= max
      # Case 1: line is not inside the blockquote, and this line is empty.
      break
    if state.src.charCodeAt(pos++) == 0x3E and !wasOutdented
      # This line is inside the blockquote.
      # skip spaces after ">" and re-calculate offset
      initial = offset = state.sCount[nextLine] + pos - (state.bMarks[nextLine] + state.tShift[nextLine])
      # skip one optional space after '>'
      if state.src.charCodeAt(pos) == 0x20
        # ' >   test '
        #     ^ -- position start of line here:
        pos++
        initial++
        offset++
        adjustTab = false
        spaceAfterMarker = true
      else if state.src.charCodeAt(pos) == 0x09
        spaceAfterMarker = true
        if (state.bsCount[nextLine] + offset) % 4 == 3
          # '  >\t  test '
          #       ^ -- position start of line here (tab has width===1)
          pos++
          initial++
          offset++
          adjustTab = false
        else
          # ' >\t  test '
          #    ^ -- position start of line here + shift bsCount slightly
          #         to make extra space appear
          adjustTab = true
      else
        spaceAfterMarker = false
      oldBMarks.push state.bMarks[nextLine]
      state.bMarks[nextLine] = pos
      while pos < max
        ch = state.src.charCodeAt(pos)
        if isSpace(ch)
          if ch == 0x09
            offset += 4 - ((offset + state.bsCount[nextLine] + (if adjustTab then 1 else 0)) % 4)
          else
            offset++
        else
          break
        pos++
      lastLineEmpty = pos >= max
      oldBSCount.push state.bsCount[nextLine]
      state.bsCount[nextLine] = state.sCount[nextLine] + 1 + (if spaceAfterMarker then 1 else 0)
      oldSCount.push state.sCount[nextLine]
      state.sCount[nextLine] = offset - initial
      oldTShift.push state.tShift[nextLine]
      state.tShift[nextLine] = pos - (state.bMarks[nextLine])
      nextLine++
      continue
    # Case 2: line is not inside the blockquote, and the last line was empty.
    if lastLineEmpty
      break
    # Case 3: another tag found.
    terminate = false
    i = 0
    l = terminatorRules.length
    while i < l
      if terminatorRules[i](state, nextLine, endLine, true)
        terminate = true
        break
      i++
    if terminate
      # Quirk to enforce "hard termination mode" for paragraphs;
      # normally if you call `tokenize(state, startLine, nextLine)`,
      # paragraphs will look below nextLine for paragraph continuation,
      # but if blockquote is terminated by another tag, they shouldn't
      state.lineMax = nextLine
      if state.blkIndent != 0
        # state.blkIndent was non-zero, we now set it to zero,
        # so we need to re-calculate all offsets to appear as
        # if indent wasn't changed
        oldBMarks.push state.bMarks[nextLine]
        oldBSCount.push state.bsCount[nextLine]
        oldTShift.push state.tShift[nextLine]
        oldSCount.push state.sCount[nextLine]
        state.sCount[nextLine] -= state.blkIndent
      break
    oldBMarks.push state.bMarks[nextLine]
    oldBSCount.push state.bsCount[nextLine]
    oldTShift.push state.tShift[nextLine]
    oldSCount.push state.sCount[nextLine]
    # A negative indentation means that this is a paragraph continuation
    #
    state.sCount[nextLine] = -1
    nextLine++
  oldIndent = state.blkIndent
  state.blkIndent = 0
  token = state.push('blockquote_open', 'blockquote', 1)
  token.markup = '>'
  token.map = lines = [
    startLine
    0
  ]
  state.md.block.tokenize state, startLine, nextLine
  token = state.push('blockquote_close', 'blockquote', -1)
  token.markup = '>'
  state.lineMax = oldLineMax
  state.parentType = oldParentType
  lines[1] = state.line
  # Restore original tShift; this might not be necessary since the parser
  # has already been here, but just to make sure we can do that.
  i = 0
  while i < oldTShift.length
    state.bMarks[i + startLine] = oldBMarks[i]
    state.tShift[i + startLine] = oldTShift[i]
    state.sCount[i + startLine] = oldSCount[i]
    state.bsCount[i + startLine] = oldBSCount[i]
    i++
  state.blkIndent = oldIndent
  true
