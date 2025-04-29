function app() {
  return {
    pinLength: 4,
    code: Array(4).fill(""),
    resetValue(i) {
      for (let j = 0; j < this.pinLength; j++) {
        if (j >= i) document.getElementById(`codefield_${j}`).value = "";
      }
    },
    stepForward(i) {
      if (
        document.getElementById(`codefield_${i}`).value &&
        i !== this.pinLength - 1
      ) {
        document.getElementById(`codefield_${i + 1}`).focus();
        document.getElementById(`codefield_${i + 1}`).value = "";
      }
    },
    stepBack(i) {
      if (i > 0) {
        this.code[i] = "";
        document.getElementById(`codefield_${i - 1}`).focus();
      }
    },
  };
}
