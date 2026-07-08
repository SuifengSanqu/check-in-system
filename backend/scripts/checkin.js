const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');
const path = require('path');

puppeteer.use(StealthPlugin());

async function readStdin() {
    return new Promise((resolve) => {
        let data = '';
        process.stdin.on('data', (chunk) => { data += chunk; });
        process.stdin.on('end', () => { resolve(JSON.parse(data)); });
    });
}

function random(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
}

async function typeHumanLike(page, selector, text, cfg) {
    const el = await page.$(selector);
    if (!el) throw new Error(`Selector not found: ${selector}`);
    await el.click({ clickCount: 3 });
    for (const char of text) {
        await page.keyboard.type(char, { delay: random(cfg.typing_delay_min, cfg.typing_delay_max) });
    }
}

async function moveMouseHumanLike(page, targetX, targetY, cfg) {
    const steps = random(cfg.mouse_steps_min, cfg.mouse_steps_max);
    const startX = random(100, cfg.viewport.width - 100);
    const startY = random(100, cfg.viewport.height - 100);

    for (let i = 0; i <= steps; i++) {
        const t = i / steps;
        const x = Math.round(startX + (targetX - startX) * (3 * t * t - 2 * t * t * t));
        const y = Math.round(startY + (targetY - startY) * (3 * t * t - 2 * t * t * t));
        await page.mouse.move(x, y);
        await sleep(random(5, 15));
    }
}

async function clickHumanLike(page, selector, cfg) {
    const el = await page.$(selector);
    if (!el) throw new Error(`Selector not found: ${selector}`);

    const box = await el.boundingBox();
    const offsetX = random(-5, 5);
    const offsetY = random(-5, 5);
    const targetX = box.x + box.width / 2 + offsetX;
    const targetY = box.y + box.height / 2 + offsetY;

    await moveMouseHumanLike(page, targetX, targetY, cfg);
    await sleep(random(cfg.click_delay_min, cfg.click_delay_max));
    await page.mouse.click(targetX, targetY);
}

async function scrollHumanLike(page, cfg) {
    const steps = random(cfg.scroll_steps_min, cfg.scroll_steps_max);
    for (let i = 0; i < steps; i++) {
        const scrollAmount = random(100, 400);
        await page.evaluate((amount) => { window.scrollBy(0, amount); }, scrollAmount);
        await sleep(random(100, 500));
    }
}

async function findAndClickByText(page, text) {
    const elements = await page.$$('*');
    for (const el of elements) {
        try {
            const txt = await page.evaluate((e) => e.textContent, el);
            if (txt && txt.includes(text)) {
                return el;
            }
        } catch (_) {}
    }
    return null;
}

async function run() {
    const params = await readStdin();
    const cfg = params.random_config;

    const browser = await puppeteer.launch({
        headless: true,
        executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || undefined,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-blink-features=AutomationControlled',
        ],
    });

    const page = await browser.newPage();

    await page.setViewport(cfg.viewport);
    await page.setUserAgent(cfg.user_agent);

    await page.evaluateOnNewDocument(() => {
        Object.defineProperty(navigator, 'webdriver', { get: () => false });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] });
    });

    try {
        await page.goto(params.login_url, { waitUntil: 'networkidle2', timeout: 30000 });
        await sleep(random(cfg.page_wait_min, cfg.page_wait_max));

        const usernameSelector = params.checkin_selector.includes('#username') ? '#username'
            : 'input[type="text"], input[name="username"], input[name="account"], input[placeholder*="账号"]';

        const passwordSelector = 'input[type="password"], input[name="password"]';

        await typeHumanLike(page, usernameSelector, params.username, cfg);
        await sleep(random(300, 800));
        await typeHumanLike(page, passwordSelector, params.password, cfg);
        await sleep(random(300, 1500));

        const loginSelectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("登录")',
            'button:has-text("登錄")',
            '.login-btn',
        ];

        let clicked = false;
        for (const sel of loginSelectors) {
            try {
                const el = await page.$(sel);
                if (el) {
                    await clickHumanLike(page, sel, cfg);
                    clicked = true;
                    break;
                }
            } catch (_) {}
        }

        if (!clicked) {
            const loginBtn = await findAndClickByText(page, '登录');
            if (loginBtn) {
                await loginBtn.click();
            }
        }

        await sleep(random(cfg.page_wait_min, cfg.page_wait_max));
        await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 }).catch(() => {});

        let checkinClicked = false;

        if (params.checkin_selector) {
            try {
                await page.waitForSelector(params.checkin_selector, { timeout: 10000 });
                await scrollHumanLike(page, cfg);
                await clickHumanLike(page, params.checkin_selector, cfg);
                checkinClicked = true;
            } catch (_) {}
        }

        if (!checkinClicked && params.checkin_text) {
            const texts = params.checkin_text.split('|');
            for (const text of texts) {
                const el = await findAndClickByText(page, text);
                if (el) {
                    await scrollHumanLike(page, cfg);
                    await el.click();
                    checkinClicked = true;
                    break;
                }
            }
        }

        if (!checkinClicked && !params.checkin_selector && !params.checkin_text) {
            const keywords = ['签到', '签 到', '签到领积分', '每日签到', '打卡', '加100', '+100'];
            for (const kw of keywords) {
                const el = await findAndClickByText(page, kw);
                if (el) {
                    await scrollHumanLike(page, cfg);
                    await el.click();
                    checkinClicked = true;
                    break;
                }
            }
        }

        await sleep(2000);

        const screenshotDir = path.resolve(__dirname, '..', 'screenshots');
        if (!fs.existsSync(screenshotDir)) fs.mkdirSync(screenshotDir, { recursive: true });
        const screenshotPath = path.join(screenshotDir, `checkin_${Date.now()}.png`);
        await page.screenshot({ path: screenshotPath, fullPage: false });

        await browser.close();

        const result = {
            status: checkinClicked ? 'success' : 'no_checkin_found',
            screenshot_path: screenshotPath,
            error: checkinClicked ? '' : 'No matching check-in button found on page',
        };
        process.stdout.write(JSON.stringify(result));
    } catch (err) {
        await browser.close();
        const result = {
            status: 'failed',
            screenshot_path: '',
            error: err.message,
        };
        process.stdout.write(JSON.stringify(result));
    }
}

run();
