
var data = source.data;
var filetext = 'section,bucket,group_A,group_B\n';

for (i=0; i < data['bucket'].length; i++) {
    var currRow = [data['section_col'][i].toString(),
                   data['bucket'][i].toString(),
                   data['group_A'][i].toString(),
                   data['group_B'][i].toString().concat('\n')];
    var joined = currRow.join();
    filetext = filetext.concat(joined);
}

var filename = "output_" + data['section_col'][0] + ".csv";
var blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' });

link = document.createElement('a')
link.href = URL.createObjectURL(blob);
link.download = filename  
link.target = "_blank";
link.style.visibility = 'hidden';
link.dispatchEvent(new MouseEvent('click'))
