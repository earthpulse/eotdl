import { test, expect } from "@playwright/test";

test.use({
  storageState: "auth.json",
});

const deleteDataset = async (request, name) => {
  return await request.delete(`http://localhost:8010/datasets/${name}`, {
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": "12345678",
    },
  });
};

test("test ingest dataset", async ({ page, request }) => {
  const name = "test-name";
  await page.goto("/datasets");
  // ingest dataset
  await page.getByText("+ Ingest dataset").click();
  await page.getByPlaceholder("Dataset name").click();
  await page.getByPlaceholder("Dataset name").fill(name);
  await page.getByPlaceholder("Dataset author").click();
  await page.getByPlaceholder("Dataset author").fill("sd");
  await page.getByPlaceholder("Link to source data").fill("a");
  await page.getByPlaceholder("Link to source data").click();
  await page.getByPlaceholder("Link to source data").fill("http://asd");
  await page.getByPlaceholder("License").click();
  await page.getByPlaceholder("License").fill("asdf");
  await page.locator("#editor div").first().fill("a");
  await page.locator("#editor div").first().click();
  await page.locator("#editor div").filter({ hasText: "a" }).fill("asdf");
  await page.getByRole("paragraph").filter({ hasText: "sentinel-2" }).click();
  await page
    .locator("input[type='file']")
    .setInputFiles(["tests/e2e/files/ARC-800-tasks.zip"]);
  await page.getByRole("button", { name: "Ingest" }).click();
  await page.waitForTimeout(3000);
  // navigate to dataset page
  await page.getByRole("link", { name }).click();
  // await page.goto("/datasets/asd");
  await expect(page).toHaveTitle(`EOTDL | ${name}`);
  // await expect(page).toHaveText(name);
  // delete dataset
  const response = await deleteDataset(request, name);
  expect(response.status()).toBe(200);
});
