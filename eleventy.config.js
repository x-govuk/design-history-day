module.exports = function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy("src/assets");
  eleventyConfig.addGlobalData("siteUrl", "https://design-history-day.x-govuk.org");
};
