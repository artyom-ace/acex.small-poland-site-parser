// -----------------------------------------------
// Scraper for "b2b.cedrus.com.pl"
// -----------------------------------------------
// INPUT: login credentials (credentialsDefaults)
// OUTPUT:
//  scraped_positions_${date}.csv
//      or
//  scraped_positions_${date}.csv
//  scraped_positions_${date}.added.csv
//  scraped_positions_${date}.removed.csv
//  scraped_positions_${date}.chnaged.csv

const needle = require('needle');
const tress = require('tress');
const cheerio = require('cheerio');
const cliProgress = require('cli-progress');
const fs = require('fs');
const path = require('path')
const csv = require('fast-csv');

// -----------------------------------------------
// consts
const url = 'https://b2b.cedrus.com.pl/logowanie';
const credentialsDefaults = {
    login: 'info@raingarden.pl',
    password: '-----'
};

const maxTreads = 10;
const optionsDefaults = {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
};

const filePrefix = 'scraped_data_';
const datePattern = /\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])/;
const fileExt = '.csv';
const dataDirectory = path.join(process.env.USERPROFILE, 'Desktop', 'Cedrus Scraped Data');
const wordPattern = /([\p{L}-]+)/u

// -----------------------------------------------
// declarations
class Good {
    constructor(code, name, price, availability) {
        this.code = code;
        this.name = name;
        this.price = price;
        this.availability = availability;
    }
}

// -----------------------------------------------
// globals
let storedCookies = null;
let data = [];

// -----------------------------------------------
// helper functions
function normalizeString(desc) {
    if (desc) {
        desc = desc.replace(/(\r\n|\n|\r|\s+|\t|&nbsp;)/gm, ' ');
        //desc = desc.replace(/"/g, '""');
        desc = desc.replace(/ +(?= )/g, '');
    }
    return desc;
}

function getFirstWord(str) {
  if ((match = wordPattern.exec(str)) !== null)
    return match[0];
  return '';
}

function compareByCode(x, y) {
    if (x.code < y.code) return -1;
    if (x.code > y.code) return 1;
    return 0;
}

function localDateStr(date) {
    const tzOffset = date.getTimezoneOffset();
    date = new Date(date.getTime() - (tzOffset * 60 * 1000));
    return date.toISOString().split('T')[0];
}

function makeFileName(date, suffix = '') {
    return filePrefix + localDateStr(date) + suffix + fileExt;
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
}

// -----------------------------------------------
// run
console.log(`access login page "${url}"...`);

needle.get(url, function (error, response) {
    if (error) throw error;
    if (response.statusCode == 200) {
        let $ = cheerio.load(response.body);
        let tokens = $('input[name=_token]', '.form-horizontal');
        if (tokens.length == 1)
            postCredentials(tokens.first().attr("value"), response.cookies);
        else
            console.log('error pasring login page ("form" with "_token" not fould)!')
    } else
        console.log('unexpected status code after:' + response.statusCode);
});

// create a new progress bar instance and use shades_classic theme
const progressBar = new cliProgress.SingleBar({}, cliProgress.Presets.shades_grey);
const codePrefix = "Kod: ";

let q = tress(function (url, done) {
    needle.get(url, { cookies: storedCookies }, function (error, response) {
        if (error) throw error;
        // console.log('start parsing...');
        // parse DOM
        let $ = cheerio.load(response.body);
        $('.row.product-main-list-row', '.products-main-list-body').each(function () {
            let _ = $(this);
            let good = new Good(normalizeString(_.find('.column.column-code').first().text()).replace(codePrefix, ''),
                normalizeString(_.find('.column.column-name > a:nth-child(2)').first().text().trim()),
                normalizeString(_.find('.column.column-price > span > div').first().text().trim()),
                getFirstWord(normalizeString(_.find('.column.column-availability > img').first().attr('title').trim())));

            // console.log(`good: ${JSON.stringify(good)}`);
            data.push(good);
        });
        // console.log('found positions:' + data.length);
        let pagination = $('div.col-sm-6:nth-child(2) > ul.pagination');
        if (pagination.length == 1) {
            let prev = pagination.find('li > a[rel="prev"]');
            let last = pagination.find('li:nth-last-child(2) > a');
            if (prev.length == 0) {
                if (last.length > 0) {
                    let lastPage = Number(last.first().text());
                    // console.log('last page:' + lastPage);
                    progressBar.start(lastPage, 2);
                    let href = last.first().attr('href');
                    let hrefTempl = href.substring(0, href.lastIndexOf('page=') + 'page='.length);
                    for (let i = 2; i < lastPage; ++i) {
                        q.push(hrefTempl + i);
                    }
                }
            }
        }
        done();
    });
}, maxTreads);

q.success = function (data) {
    progressBar.update(q.finished.length + 1)
};

q.drain = function () {
    progressBar.stop();

    // create dir if not exist
    if (!fs.existsSync(dataDirectory))
        fs.mkdirSync(dataDirectory);

    let filePath = path.join(dataDirectory, makeFileName(new Date));

    Promise.allSettled(
        [ writeData(filePath, data), readPrevData().then(prevData => generateDiff(prevData, data)) ]
    ).then(results => {
        for(const result of results) {
            if (result.status == 'rejected') {
                if (typeof result.reason == 'string')
                    console.error(`${result.reason}`);
                else
                    console.error(`Error happened: ${result.reason}`);
            }
        }
        console.log("Done!");
    });
}

// -----------------------------------------------
// implementation

function postCredentials(token, cookies) {
    let credentials = Object.assign({ _token: token }, credentialsDefaults);
    let options = Object.assign(optionsDefaults, { cookies });
    console.log(`login with credentials:\n${JSON.stringify(credentials, null, '\t')}...`);
    needle.post(url, credentials, options, function (error, response) {
        if (error) throw error;
        if (response.statusCode == 302) {
            storedCookies = response.cookies;
            q.push(response.headers.location);
        } else
            console.log('unexpected status code after:' + response.statusCode);
    });
}

function writeData(filePath, data)
{
    return new Promise((resolve, reject) => {
        console.log(`Found data (${data.length} rows). Writinig to "${filePath}"...`);
        csv.writeToPath(filePath, data, {
            delimiter: ';',
            headers: true,
            writeBOM: true,
            transform: function (row) {
                // you could eliminate this block by changing the property names in the church objects
                return {
                    code: row.code,
                    name: row.name,
                    price: row.price,
                    availability: row.availability
                };
            }
        })
        .on('error', reject)
        .on('finish', resolve);
    });
}

function readPrevData() {
    return new Promise((resolve, reject) => {
        let fileName = getPrevCsvFileName();
        if (fileName === undefined) {
            throw 'There are no previous scraped data, diff-files are not generated!';
        }

        let filePath = path.join(dataDirectory, fileName);
        let data = [];

        //
        console.log(`Read previous scraped data from "${filePath}"`);
        fs.createReadStream(filePath)
            .pipe(csv.parse({
                delimiter: ';',
                headers: true
            })
            )
            .on('error', reject)
            .on('data', function (row) {
                data.push(new Good(row.code, row.name, row.price, getFirstWord(row.availability)));
            })
            .on('end', () => resolve(data) );
    });
}

function getPrevCsvFileName() {
    const fileNamePattern = new RegExp(`^${escapeRegExp(filePrefix)}${datePattern.source}${escapeRegExp(fileExt)}$`);

    let files = fs.readdirSync(dataDirectory);
    let csvList = files.filter(name => fileNamePattern.test(name));
    csvList.sort();

    let fileName = makeFileName(new Date);
    while (csvList.length >= 0) {
        if (csvList[csvList.length - 1] != fileName)
            break;
        csvList.pop();
    }
    return csvList[csvList.length - 1];
}

function generateDiff(prevData, data) {
    prevData.sort(compareByCode);
    data.sort(compareByCode);

    // console.log('prevData:' + prevData.length);
    // console.log('data:' + data.length);

    let removedItems = [];
    let addedItems = [];
    let changedItems = [];

    let prevIdx = 0;
    let idx = 0;
    while (prevIdx < prevData.length && idx < data.length) {
        let prevGood = prevData[prevIdx];
        let good = data[idx];
        let cmp = compareByCode(prevGood, good);
        if (cmp < 0) {
            removedItems.push(prevGood);
            ++prevIdx;
        } else if (cmp > 0) {
            addedItems.push(good);
            ++idx;
        } else {
            if (prevGood.availability != good.availability || good.price != prevGood.price) {
                changedItems.push(good);
            }
            ++prevIdx;
            ++idx;
        }
    }

    removedItems = removedItems.concat(prevData.slice(prevIdx));
    addedItems = addedItems.concat(data.slice(idx));

    // console.log('removed items:', removedItems);
    // console.log('added items:', addedItems);
    // console.log('changed items:', changedItems);

    let jobs = [
        { data: removedItems, description: 'removed' },
        { data: addedItems, description: 'added' },
        { data: changedItems, description: 'changed' }
    ].map(item => {
        new Promise((resolve, reject) => {
            const filePath = path.join(dataDirectory, makeFileName(new Date, '-' + item.description));
            console.log(`Found ${item.description} data (${item.data.length} rows). Writinig to "${filePath}"...`);
            csv.writeToPath(filePath, item.data, {
                delimiter: ';',
                headers: true,
                writeBOM: true,
                transform: function (row) {
                    // you could eliminate this block by changing the property names in the church objects
                    return {
                        code: row.code,
                        name: row.name,
                        price: row.price,
                        availability: row.availability
                    };
                }
            })
            .on('error', reject)
            .on('finish', resolve);
        });
    });

    return Promise.all(jobs);
}
