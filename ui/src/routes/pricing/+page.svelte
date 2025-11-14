<script>
    let isResearch = $state(false);

    const plans = {
        free: {
            name: "Free",
            commercial: { price: 0 },
            research: { price: 0 },
            features: [
                "5 GB storage (only public datasets/models)",
                "Workspace CPU (1 vCPU / 4 GB RAM)",
                "Maximum egress of 1 GB",
            ],
        },
        basic: {
            name: "Basic",
            commercial: { price: 500 },
            research: { price: 450 },
            features: [
                "100 GB storage (public and private datasets/models)",
                "Workspace CPU (4 vCPU / 16 GB RAM)",
                "50 GPU hours/month available (large-scale inference / fast training)*",
                "Concurrent deployment of up to 1 active model",
                "Maximum egress of 20 GB",
            ],
        },
        pro: {
            name: "Pro",
            commercial: { price: 1629 },
            research: { price: 1466.1 },
            features: [
                "500 GB storage (public and private datasets/models)",
                "Workspace CPU (12 vCPU / 48 GB RAM)",
                "100 GPU hours/month (large-scale inference / fast training)*",
                "Concurrent deployment of up to 3 active models",
                "Maximum egress of 100 GB",
            ],
        },
    };

    const addons = [
        {
            name: "Additional storage (+100GB)",
            pricingModel: "Per 100GB per month",
            commercial: { price: 20, unit: "/mo" },
            research: { price: 18, unit: "/mo" },
        },
        {
            name: "[1 x T4] GPU cloud workspace",
            pricingModel: "Per hour",
            commercial: { price: 1.5, unit: "" },
            research: { price: 1.35, unit: "" },
        },
        {
            name: "[2 x T4] Multi-GPU cloud workspace",
            pricingModel: "Per hour",
            commercial: { price: 3, unit: "" },
            research: { price: 2.7, unit: "" },
        },
        {
            name: "[4 x T4] Multi-GPU cloud workspace",
            pricingModel: "Per hour",
            commercial: { price: 4.5, unit: "" },
            research: { price: 5, unit: "" },
        },
        {
            name: "STAC metadata validation",
            pricingModel: "Per package",
            commercial: { price: 1000, unit: "" },
            research: { price: 900, unit: "" },
        },
        {
            name: "Training Course (webinar)",
            pricingModel: "Per hour",
            commercial: { price: 108, unit: "" },
            research: null,
        },
        {
            name: "Benchmark dataset generation**",
            pricingModel: "Per package",
            commercial: {
                bronze: { price: 700, description: "Up to 100GB" },
                silver: { price: 1000, description: "Up to 500 GB" },
                gold: { price: 1300, description: "Up to 1TB" },
            },
            research: {
                bronze: { price: 630, description: "Up to 100GB" },
                silver: { price: 900, description: "Up to 500 GB" },
                gold: { price: 1197, description: "Up to 1TB" },
            },
        },
        {
            name: "Challenge-as-a-service",
            pricingModel: "Per package",
            commercial: {
                bronze: { price: 5000, description: "Up to 10 usr/mo" },
                silver: { price: 8000, description: "Up to 50 usr/mo" },
                gold: { price: 13400, description: "Up to 100 usr/mo" },
            },
            research: {
                bronze: { price: 4500, description: "Up to 10 usr/mo" },
                silver: { price: 7200, description: "Up to 50 usr/mo" },
                gold: { price: 12060, description: "Up to 100 usr/mo" },
            },
        },
        {
            name: "Labelling campaign",
            pricingModel: "Per package",
            commercial: {
                bronze: { price: 2700, description: "Up to 100GB" },
                silver: { price: 4400, description: "Up to 500 GB" },
                gold: { price: 520, description: "Up to 1TB" },
            },
            research: {
                bronze: { price: 2430, description: "Up to 100GB" },
                silver: { price: 3600, description: "Up to 500 GB" },
                gold: { price: 4750, description: "Up to 1TB" },
            },
        },
        {
            name: "Advanced feature engineering",
            pricingModel: "Per package",
            commercial: {
                bronze: { price: 680, description: "Up to 10 expert h" },
                silver: { price: 2700, description: "Up to 40 expert h" },
                gold: { price: 6600, description: "Up to 100 expert h" },
            },
            research: {
                bronze: { price: 512, description: "Up to 10 expert h" },
                silver: { price: 2430, description: "Up to 40 expert h" },
                gold: { price: 5940, description: "Up to 100 expert h" },
            },
        },
    ];

    let currentPricing = $derived(isResearch ? "research" : "commercial");

    function formatPrice(price) {
        if (price === 0) return "€0";
        // Check if price has decimal places
        const hasDecimals = price % 1 !== 0;
        return `€${price.toLocaleString("en-US", {
            minimumFractionDigits: hasDecimals ? 2 : 0,
            maximumFractionDigits: hasDecimals ? 2 : 0,
        })}`;
    }
</script>

<div class="w-full flex flex-col items-center justify-between h-full grow">
    <div
        class="px-3 py-10 mt-10 w-full max-w-6xl flex flex-col items-center h-full"
    >
        <!-- Header -->
        <div class="flex flex-col justify-between mb-8 w-full gap-4">
            <h1 class="font-bold text-3xl">Pricing</h1>
            <p class="text-gray-600">
                Choose the plan that fits your needs. All plans include access
                to our platform and community support.
            </p>
        </div>

        <!-- Pricing Toggle -->
        <div class="flex items-center justify-center mb-8 w-full pt-4">
            <fieldset
                class="fieldset bg-base-100 border-base-300 rounded-box border p-4"
            >
                <legend class="fieldset-legend">Pricing Type</legend>
                <div class="flex items-center gap-4">
                    <span
                        class="text-sm {!isResearch
                            ? 'font-semibold'
                            : 'text-gray-500'}">Commercial</span
                    >
                    <label class="apple-toggle">
                        <input type="checkbox" bind:checked={isResearch} />
                        <span class="apple-toggle-slider"></span>
                    </label>
                    <span
                        class="text-sm {isResearch
                            ? 'font-semibold'
                            : 'text-gray-500'}">Research Discount</span
                    >
                </div>
            </fieldset>
        </div>

        <!-- Pricing Plans -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-6 w-full mb-12 pt-8">
            {#each Object.values(plans) as plan}
                <div
                    class="border border-gray-200 shadow-lg p-6 rounded-lg flex flex-col justify-between h-full {plan.name ===
                    'Basic'
                        ? 'ring-2 ring-blue-500 scale-105'
                        : ''}"
                >
                    <div class="text-left">
                        <h2 class="font-bold mb-2 mt-0 text-2xl">
                            {plan.name}
                        </h2>
                        <div class="mb-4">
                            <span class="text-4xl font-bold">
                                {formatPrice(plan[currentPricing].price)}
                            </span>
                            {#if plan[currentPricing].price > 0}
                                <span class="text-gray-500 text-sm"
                                    >/ month</span
                                >
                            {/if}
                        </div>
                        <ul class="space-y-2 mb-4">
                            {#each plan.features as feature}
                                <li class="flex items-start text-sm gap-2">
                                    <svg
                                        class="w-5 h-5 text-black flex-shrink-0 mt-0.5"
                                        fill="currentColor"
                                        viewBox="0 0 20 20"
                                        aria-hidden="true"
                                        style="min-width: 1.25rem; min-height: 1.25rem;"
                                    >
                                        <path
                                            fill-rule="evenodd"
                                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                            clip-rule="evenodd"
                                        />
                                    </svg>
                                    <span class="flex-1">{feature}</span>
                                </li>
                            {/each}
                        </ul>
                    </div>
                    {#if plan.name === "Free"}
                        <a
                            href="/"
                            class="btn {plan.name === 'Basic'
                                ? 'btn-primary'
                                : 'btn-outline'} w-full mt-4 flex items-center justify-center"
                        >
                            Get Started
                        </a>
                    {:else}
                        <a
                            href="mailto:support@eotld.com?subject=EOTDL%20-%20{plan.name}%20Subscription"
                            class="btn {plan.name === 'Basic'
                                ? 'btn-primary'
                                : 'btn-outline'} w-full mt-4 flex items-center justify-center"
                        >
                            Choose Plan
                        </a>
                    {/if}
                </div>
            {/each}
        </div>

        <!-- Important Notes -->
        <div
            class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-12 w-full"
        >
            <h3 class="font-semibold mb-2 text-sm">Important Notes:</h3>
            <ul class="text-sm text-gray-700 space-y-1">
                <li>
                    <strong>Data retention:</strong> 30 days after end of plan; after
                    this period, all data will be permanently deleted. This policy
                    applies to private workspaces and private datasets.
                </li>
                <li>
                    <strong>Soft quote:</strong> A soft quote policy applies to storage
                    limits, as well as to every request for instance allocation (CPU/GPU
                    resources) and other usage-based resources.
                </li>
            </ul>
        </div>

        <!-- Addons Section -->
        <div class="flex flex-col justify-between mb-6 w-full gap-4">
            <h2 class="font-bold text-3xl">Add-ons</h2>
            <p class="text-gray-600">
                Enhance your plan with additional resources and features as
                needed.
            </p>
        </div>

        <div class="overflow-x-auto w-full mb-8">
            <table class="table w-full">
                <thead>
                    <tr>
                        <th>Add-on</th>
                        <th>Unit</th>
                        <th class="text-right">Price (EUR)</th>
                        <th class="text-right">Bronze</th>
                        <th class="text-right">Silver</th>
                        <th class="text-right">Gold</th>
                    </tr>
                </thead>
                <tbody>
                    {#each addons as addon}
                        <tr>
                            <td>
                                <div class="font-bold">{addon.name}</div>
                            </td>
                            <td>
                                <div class="text-sm text-gray-600">
                                    {addon.pricingModel}
                                </div>
                            </td>
                            <td class="text-right">
                                {#if addon[currentPricing] && typeof addon[currentPricing] === "object" && "price" in addon[currentPricing]}
                                    <div
                                        class="flex flex-row items-end gap-2 justify-end align-middle"
                                    >
                                        <span class="text-lg font-bold">
                                            {formatPrice(
                                                addon[currentPricing].price,
                                            )}
                                        </span>
                                        {#if addon[currentPricing].unit}
                                            <span
                                                class="text-gray-500 text-sm self-center"
                                            >
                                                {addon[currentPricing].unit}
                                            </span>
                                        {/if}
                                    </div>
                                {:else}
                                    <span class="text-gray-400">N/A</span>
                                {/if}
                            </td>
                            <td class="text-right">
                                {#if addon[currentPricing] && typeof addon[currentPricing] === "object" && "bronze" in addon[currentPricing]}
                                    <div class="flex flex-col items-end">
                                        <span class="text-lg font-bold">
                                            {formatPrice(
                                                addon[currentPricing].bronze
                                                    .price,
                                            )}
                                        </span>
                                        <span class="text-gray-500 text-xs">
                                            {addon[currentPricing].bronze
                                                .description}
                                        </span>
                                    </div>
                                {:else}
                                    <span class="text-gray-400">N/A</span>
                                {/if}
                            </td>
                            <td class="text-right">
                                {#if addon[currentPricing] && typeof addon[currentPricing] === "object" && "silver" in addon[currentPricing]}
                                    <div class="flex flex-col items-end">
                                        <span class="text-lg font-bold">
                                            {formatPrice(
                                                addon[currentPricing].silver
                                                    .price,
                                            )}
                                        </span>
                                        <span class="text-gray-500 text-xs">
                                            {addon[currentPricing].silver
                                                .description}
                                        </span>
                                    </div>
                                {:else}
                                    <span class="text-gray-400">N/A</span>
                                {/if}
                            </td>
                            <td class="text-right">
                                {#if addon[currentPricing] && typeof addon[currentPricing] === "object" && "gold" in addon[currentPricing]}
                                    <div class="flex flex-col items-end">
                                        <span class="text-lg font-bold">
                                            {formatPrice(
                                                addon[currentPricing].gold
                                                    .price,
                                            )}
                                        </span>
                                        <span class="text-gray-500 text-xs">
                                            {addon[currentPricing].gold
                                                .description}
                                        </span>
                                    </div>
                                {:else}
                                    <span class="text-gray-400">N/A</span>
                                {/if}
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>
            <p class="text-sm text-gray-600 mt-4">
                **After generation, the dataset is stored in the user's private
                storage area. If the plan's included storage is exceeded, the
                user must procure additional storage.
            </p>
        </div>
    </div>

    <!-- Sponsorship CTA -->
    <div
        class="px-3 w-full mb-12 mt-12 m-auto max-w-6xl flex flex-col items-center justify-center"
    >
        <div
            class="sponsorship-cta-card flex flex-col items-center justify-center w-full px-8 py-10 rounded-2xl border border-blue-200 shadow-md bg-gradient-to-br from-blue-50 via-white to-blue-100"
        >
            <h2 class="font-bold text-3xl mb-2 text-blue-800">
                Need sponsorship?
            </h2>
            <p class="px-3 mb-4 text-gray-700 max-w-xl text-center">
                We can sponsor your research activities. Tell us about your
                project and we'll work out a custom plan.
            </p>
            <a
                href="mailto:support@eotld.com?subject=Research%20sponsorship"
                class="btn btn-primary shadow transition hover:scale-105"
                style="min-width: 160px;">Get in touch</a
            >
        </div>
    </div>
</div>

<style>
    .sponsorship-cta-card {
        /* fallback for browsers that don't support gradients */
        background-color: #f8fafc;
    }
    /* If you want a little extra border effect on the card, you can add: */
    .sponsorship-cta-card {
        box-shadow: 0 6px 24px 0 rgba(52, 120, 246, 0.08);
        /* The gradient is handled by Tailwind classes, but this is left here for clarity */
    }
    .apple-toggle {
        position: relative;
        display: inline-block;
        width: 51px;
        height: 31px;
    }

    .apple-toggle input {
        opacity: 0;
        width: 0;
        height: 0;
    }

    .apple-toggle-slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #ccc;
        transition: 0.3s;
        border-radius: 34px;
    }

    .apple-toggle-slider:before {
        position: absolute;
        content: "";
        height: 27px;
        width: 27px;
        left: 2px;
        bottom: 2px;
        background-color: white;
        transition: 0.3s;
        border-radius: 50%;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    .apple-toggle input:checked + .apple-toggle-slider {
        background-color: #34c759;
    }

    .apple-toggle input:checked + .apple-toggle-slider:before {
        transform: translateX(20px);
    }

    .apple-toggle input:focus + .apple-toggle-slider {
        box-shadow: 0 0 1px #34c759;
    }

    .apple-toggle input:active + .apple-toggle-slider:before {
        width: 35px;
    }

    .apple-toggle input:checked:active + .apple-toggle-slider:before {
        transform: translateX(16px);
    }
</style>
