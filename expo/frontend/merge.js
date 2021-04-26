var merge = require('package-merge');
var dst = fs.readFileSync('package.json');
var src = fs.readFileSync('package.2.json');
 
// Create a new `package.json`
// console.log(merge(dst, src))
