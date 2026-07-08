const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');
const path = require('path');

puppeteer.use(StealthPlugin());

// ─── helpers ────────────────────────────────────────────────

async function readStdin() {
    return new Promise((resolve) => {
        let data = '';
        process.stdin.on('data', (chunk) => { data += chunk; });
        process.stdin.on('end', () => { resolve(JSON.parse(data)); });
    });
}

function random(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }

async function typeHumanLike(page, selector, text, cfg) {
    const el = await page.waitForSelector(selector, { timeout: 10000 });
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
    const el = await page.waitForSelector(selector, { timeout: 10000 });
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
                await el.click();
                return true;
            }
        } catch (_) {}
    }
    return false;
}

async function tryDismissPopup(page, selector, cfg) {
    try {
        const el = await page.waitForSelector(selector, { timeout: 3000 });
        if (el) {
            await sleep(random(300, 800));
            await clickHumanLike(page, selector, cfg);
            await sleep(random(500, 1000));
            return true;
        }
    } catch (_) {}
    return false;
}

// ─── step: dismiss all popups / cookie banners ─────────────

async function dismissPopups(page, cfg, params) {
    const popupSelectors = params.popup_selectors || [];
    const cookieSelector = params.cookie_banner_selector || '';

    const commonCookieSelectors = [
        cookieSelector,
        '.cookie-accept', '.cookie-consent button', '[aria-label*="cookie" i] button',
        '.gdpr-accept', '#onetrust-accept-btn-handler',
        'button:has-text("同意")', 'button:has-text("Accept")',
        'button:has-text("知道了")', 'button:has-text("Got it")',
    ].filter(Boolean);

    for (const sel of commonCookieSelectors) {
        await tryDismissPopup(page, sel, cfg);
    }

    for (const sel of popupSelectors) {
        await tryDismissPopup(page, sel, cfg);
    }

    const genericCloseSelectors = [
        '.modal-close', '[aria-label="关闭"]', '.dialog-close',
        'button:has-text("关闭")', 'button:has-text("跳过")',
        '.overlay-close', '[data-dismiss="modal"]',
    ];
    for (const sel of genericCloseSelectors) {
        await tryDismissPopup(page, sel, cfg);
    }
}

// ─── step: single-page login ───────────────────────────────

async function singlePageLogin(page, params, cfg) {
    const usernameSel = params.login_username_selector || guessUsernameSelector();
    const passwordSel = params.login_password_selector || guessPasswordSelector();

    await typeHumanLike(page, usernameSel, params.username, cfg);
    await sleep(random(300, 800));
    await typeHumanLike(page, passwordSel, params.password, cfg);
    await sleep(random(300, 1500));

    await clickLoginButton(page, params, cfg);
}

// ─── step: two-step login (username -> next -> password) ───

async function twoStepLogin(page, params, cfg) {
    const usernameSel = params.login_username_selector || guessUsernameSelector();
    await typeHumanLike(page, usernameSel, params.username, cfg);
    await sleep(random(300, 800));

    const nextSelectors = [
        params.login_button_selector,
        'button:has-text("下一步")', 'button:has-text("Next")',
        'button:has-text("继续")', 'button:has-text("Continue")',
        'input[type="submit"]', 'button[type="submit"]',
    ].filter(Boolean);

    let nextClicked = false;
    for (const sel of nextSelectors) {
        try {
            await clickHumanLike(page, sel, cfg);
            nextClicked = true;
            break;
        } catch (_) {}
    }
    if (!nextClicked) {
        await findAndClickByText(page, '下一步') || await findAndClickByText(page, 'Next');
    }
    await sleep(random(1000, 3000));
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 }).catch(() => {});

    const passwordSel = params.login_password_selector || guessPasswordSelector();
    await typeHumanLike(page, passwordSel, params.password, cfg);
    await sleep(random(300, 1500));

    await clickLoginButton(page, params, cfg);
}

// ─── helpers: guess selectors ──────────────────────────────

function guessUsernameSelector() {
    return [
        'input[type="text"]', 'input[type="email"]', 'input[name="username"]',
        'input[name="account"]', 'input[name="email"]', 'input[name="phone"]',
        'input[placeholder*="账号"]', 'input[placeholder*="邮箱"]', 'input[placeholder*="手机"]',
        'input[placeholder*="用户"]', 'input[id*="username" i]', 'input[id*="account" i]',
    ].join(', ');
}

function guessPasswordSelector() {
    return [
        'input[type="password"]', 'input[name="password"]',
        'input[placeholder*="密码"]', 'input[id*="password" i]',
    ].join(', ');
}

async function clickLoginButton(page, params, cfg) {
    const loginSelectors = [
        params.login_button_selector,
        'button[type="submit"]', 'input[type="submit"]',
        'button:has-text("登录")', 'button:has-text("登錄")',
        'button:has-text("登 录")', 'button:has-text("Sign in")',
        'button:has-text("Log in")', '.login-btn', '#login-btn',
        'a:has-text("登录")', '.btn-login',
    ].filter(Boolean);

    for (const sel of loginSelectors) {
        try {
            await clickHumanLike(page, sel, cfg);
            return;
        } catch (_) {}
    }

    const found = await findAndClickByText(page, '登录') || await findAndClickByText(page, 'Log in');
    if (!found) throw new Error('Could not find login button');
}

// ─── step: post-login navigation ───────────────────────────

async function navigateToCheckinPage(page, params, cfg) {
    if (params.checkin_nav_url) {
        await sleep(random(cfg.page_wait_min, cfg.page_wait_max));
        await page.goto(params.checkin_nav_url, { waitUntil: 'networkidle2', timeout: 30000 });
        await sleep(random(cfg.page_wait_min, cfg.page_wait_max));
    }

    await dismissPopups(page, cfg, params);
}

// ─── step: execute pre-checkin extra steps ──────────────────

async function executeExtraSteps(page, steps, cfg) {
    for (const step of steps) {
        switch (step.action) {
            case 'click': {
                await scrollHumanLike(page, cfg);
                await clickHumanLike(page, step.selector, cfg);
                break;
            }
            case 'wait': {
                await sleep(step.ms || 1000);
                break;
            }
            case 'scroll': {
                await scrollHumanLike(page, cfg);
                break;
            }
            case 'type': {
                await typeHumanLike(page, step.selector, step.value, cfg);
                break;
            }
            case 'navigate': {
                await page.goto(step.url, { waitUntil: 'networkidle2', timeout: 30000 });
                break;
            }
            case 'evaluate': {
                await page.evaluate(step.code);
                break;
            }
        }
        await sleep(random(200, 500));
    }
}

// ─── step: click check-in button ────────────────────────────

async function executeCheckin(page, params, cfg) {
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
            await scrollHumanLike(page, cfg);
            if (await findAndClickByText(page, text.trim())) {
                checkinClicked = true;
                break;
            }
        }
    }

    if (!checkinClicked) {
        const keywords = ['签到', '签 到', '签到领积分', '每日签到', '打卡', '加100', '+100', 'Check in', 'Daily'];
        for (const kw of keywords) {
            await scrollHumanLike(page, cfg);
            if (await findAndClickByText(page, kw)) {
                checkinClicked = true;
                break;
            }
        }
    }

    return checkinClicked;
}

// ─── main ───────────────────────────────────────────────────

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

    let checkinClicked = false;
    const errors = [];

    try {
        // 1. navigate to login page
        await page.goto(params.login_url, { waitUntil: 'networkidle2', timeout: 30000 });
        await sleep(random(cfg.page_wait_min, cfg.page_wait_max));

        // 2. dismiss popups/banners on login page
        await dismissPopups(page, cfg, params);

        // 3. login
        if (params.login_flow === 'two_step') {
            await twoStepLogin(page, params, cfg);
        } else {
            await singlePageLogin(page, params, cfg);
        }

        // 4. wait for login redirect
        await sleep(random(cfg.page_wait_min, cfg.page_wait_max));
        await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 }).catch(() => {});

        // 5. dismiss any post-login popups
        await dismissPopups(page, cfg, params);

        // 6. navigate to check-in page if needed
        await navigateToCheckinPage(page, params, cfg);

        // 7. execute pre-checkin steps
        let extraSteps = [];
        if (params.checkin_extra_steps) {
            try { extraSteps = JSON.parse(params.checkin_extra_steps); } catch (_) {}
        }
        await executeExtraSteps(page, extraSteps, cfg);

        // 8. click check-in button
        checkinClicked = await executeCheckin(page, params, cfg);
    } catch (err) {
        errors.push(err.message);
    }

    // screenshot
    let screenshotPath = '';
    try {
        const screenshotDir = path.resolve(__dirname, '..', 'screenshots');
        if (!fs.existsSync(screenshotDir)) fs.mkdirSync(screenshotDir, { recursive: true });
        screenshotPath = path.join(screenshotDir, `checkin_${Date.now()}.png`);
        await page.screenshot({ path: screenshotPath, fullPage: false });
    } catch (_) {}

    await browser.close();

    let status, errorMsg;
    if (errors.length > 0) {
        status = 'failed';
        errorMsg = errors.join('; ');
    } else if (checkinClicked) {
        status = 'success';
        errorMsg = '';
    } else {
        status = 'no_checkin_found';
        errorMsg = 'No matching check-in button found on page';
    }

    process.stdout.write(JSON.stringify({
        status,
        screenshot_path: screenshotPath,
        error: errorMsg,
    }));
}

run();
