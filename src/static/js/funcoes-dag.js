var dagfuncs = window.dashAgGridFunctions = window.dashAgGridFunctions || {};


dagfuncs.FMT = function (number) {
    if (typeof number === 'number') {
        return number.toLocaleString('pt-br')
    }
    return number
}