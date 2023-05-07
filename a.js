const puppeteer = require("puppeteer-extra");
const StealthPlugin = require("puppeteer-extra-plugin-stealth");

puppeteer.use(StealthPlugin());

const from = "Seattle";
const to = "Las Vegas";
const leaveDate = "5-15-2023"; // mm-dd-yyyy format
const returnDate = "5-18-2023"; // mm-dd-yyyy format
const URL = `https://www.google.com/travel/flights?hl=en-US&curr=USD`;

async function getFlightsFromPage(page) {
  return await page.evaluate(() =>
    Array.from(document.querySelectorAll(".pIav2d")).map((el) => {
      const thumbnailString = el.querySelector(".EbY4Pc")?.getAttribute("style");
      const startIndex = thumbnailString?.indexOf("url(");
      const endIndex = thumbnailString?.indexOf(";");
      const thumbnail = thumbnailString?.slice(startIndex + 4, endIndex - 1).replaceAll("\\", "") || "No thumbnail";
      const layover = el.querySelector(".BbR8Ec .sSHqwe")?.getAttribute("aria-label");
      return {
        thumbnail,
        companyName: el.querySelector(".Ir0Voe .sSHqwe")?.textContent.trim(),
        description: el.querySelector(".mv1WYe")?.getAttribute("aria-label"),
        duration: el.querySelector(".gvkrdb")?.textContent.trim(),
        airportLeave: el.querySelectorAll(".Ak5kof .sSHqwe .eoY5cb")[0]?.textContent.trim(),
        airportArive: el.querySelectorAll(".Ak5kof .sSHqwe .eoY5cb")[1]?.textContent.trim(),
        layover: layover || "Nonstop",
        emisions: el.querySelector(".V1iAHe > div")?.getAttribute("aria-label").replace(". Learn more about this emissions estimate", " "),
        price: el.querySelector(".U3gSDe .YMlIz > span")?.textContent.trim(),
        priceDescription: el.querySelector(".U3gSDe .JMnxgf > span > span > span")?.getAttribute("aria-label"),
      };
    })
  );
}

async function getFlightsResults() {
  const browser = await puppeteer.launch({
    headless: false, // if you want to see what the browser is doing, you need to change this option to "false"
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });

  const page = await browser.newPage();
  page.setViewport({
    width: 800,
    height: 720,
  });

  await page.setDefaultNavigationTimeout(90000);
  await page.goto(URL);

  await page.waitForSelector(".e5F5td");
  const inputs = await page.$$(".e5F5td");
  // type "from"
  await inputs[0].click();
  await page.waitForTimeout(3000);
  await page.keyboard.type(from);
  await page.keyboard.press("Enter");
  // type "to"
  await inputs[1].click();
  await page.waitForTimeout(1000);
  await page.keyboard.type(to);
  await page.waitForTimeout(3000);
  await page.keyboard.press("Enter");
  await page.waitForTimeout(1000);
  // type "Leave date"
  await page.waitForSelector('[aria-label="Departure"]', {visible: true});
  const departureField = await page.$('[aria-label="Departure"]');
  await departureField.click({delay: 100});
  await page.waitForTimeout(1000);
  await page.keyboard.type(leaveDate);
  await page.waitForTimeout(3000);
  await page.keyboard.press("Enter");
  await page.waitForTimeout(1000);

  // type "Return date"
  await page.waitForSelector('[aria-label="Return"]', {visible: true});
  const returnField = await page.$('[aria-label="Return"]');
  await returnField.click({delay: 100});
  await page.waitForTimeout(1000);
  await page.keyboard.type(returnDate);
  await page.waitForTimeout(1000);
  await page.keyboard.press("Enter");
  await page.waitForTimeout(1000);
  // choose "One way"
  

  // press "Done"
// press "Done"
// press "Done"
await page.waitForSelector(".VfPpkd-LgbsSe-OWXEXe-k8QpJ", { visible: true, timeout: 30000 });
await page.click(".VfPpkd-LgbsSe-OWXEXe-k8QpJ");
await page.waitForTimeout(1000);
await page.keyboard.press("Enter");


  // press "Search"
  await page.waitForTimeout(1000);
  await page.keyboard.press("Enter");

  await page.waitForSelector('[aria-label="Search"]', { visible: true, timeout: 30000 });
  const searchButton = await page.$('[aria-label="Search"]');
  await searchButton.click({delay: 100});
  await page.waitForTimeout(2000);
  // await page.keyboard.press("Enter");

  const moreButton = await page.$(".XsapA");
  if (moreButton) {
    await moreButton.click();
    await page.waitForTimeout(3000);
  }

  const flights = await getFlightsFromPage(page);

  await browser.close();

  return flights;
}

getFlightsResults().then(console.log)