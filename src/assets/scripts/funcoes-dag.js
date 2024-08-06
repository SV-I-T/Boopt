var dagfuncs = window.dashAgGridFunctions = window.dashAgGridFunctions || {};


dagfuncs.FMT = function (number) {
    console.log(number);
    if (typeof number === 'number') {
        return number.toLocaleString('pt-br')
    }
    return number
}