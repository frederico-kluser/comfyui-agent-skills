#!/usr/bin/env python3
"""
Convert ComfyUI UI-format workflow JSON to API-format JSON.

Maps node inputs (widget values + linked inputs) to the flat API format:
  { node_id: { class_type, inputs: { name: value | [src_node, src_slot] } } }

Usage:
  python convert_to_api.py workflow_ui.json > workflow_api.json
  python convert_to_api.py workflow_ui.json workflow_api.json
"""

import json
import sys


def convert_to_api(data: dict) -> dict:
    """Convert a ComfyUI UI-format workflow to API format."""
    nodes_by_id = {n["id"]: n for n in data.get("nodes", [])}
    links = data.get("links", [])

    # Build link lookup: (dst_node_id, dst_input_slot) → [src_node_str, src_output_slot]
    link_map = {}
    for l in links:
        # link format: [link_id, src_node, src_slot, dst_node, dst_slot, type]
        link_map[(l[3], l[4])] = [str(l[1]), l[2]]

    api = {}

    for node_id, node in nodes_by_id.items():
        class_type = node["type"]
        node_inputs = node.get("inputs", [])
        widgets_values = node.get("widgets_values", {})

        api_inputs = {}

        # ── Phase 1: Process each entry in the node's "inputs" array ──
        # Each entry has: name, type, optional: widget{name}, optional: link
        widget_idx = 0  # tracks position in widgets_values list

        for inp in node_inputs:
            inp_name = inp["name"]
            link_id = inp.get("link")
            has_widget = "widget" in inp

            # Case A: This input is connected via a link → use link reference
            if link_id is not None:
                for l in links:
                    if l[0] == link_id:
                        api_inputs[inp_name] = [str(l[1]), l[2]]
                        break
                continue

            # Case B: This is a widget input (has a "widget" sub-object)
            if has_widget and isinstance(widgets_values, list):
                widget_info = inp["widget"]
                widget_name = widget_info.get("name", inp_name) if isinstance(widget_info, dict) else inp_name

                if widget_idx < len(widgets_values):
                    val = widgets_values[widget_idx]
                    # Clean dict values (VHS nodes)
                    if isinstance(val, dict):
                        clean = {k: v for k, v in val.items()
                                 if k not in ("videopreview", "params")}
                        if clean:
                            # For VHS: flatten video/filename into the input name
                            api_inputs[inp_name] = clean.get("video", clean.get("filename", clean))
                        else:
                            api_inputs[inp_name] = ""
                    else:
                        api_inputs[inp_name] = val
                widget_idx += 1
                continue

            # Case C: Neither linked nor a widget — skip (e.g., optional model inputs)
            # Some inputs like "meta_batch" or "vae" are optional and link-only
            # Only include if it has a link reference in link_map
            inp_key = (node_id, node_inputs.index(inp))
            if inp_key in link_map:
                api_inputs[inp_name] = link_map[inp_key]

        # ── Phase 2: Handle nodes with NO "inputs" array ──
        # These nodes (LoadImage, MarkdownNote, etc.) have only widgets_values
        if not node_inputs:
            if isinstance(widgets_values, list):
                # LoadImage: widgets_values = [filename, upload_mode]
                # SaveImage: handled via inputs array
                if class_type == "LoadImage":
                    if widgets_values:
                        api_inputs["image"] = widgets_values[0]
                elif class_type == "MarkdownNote":
                    pass  # No API inputs needed
                elif class_type == "PrimitiveInt":
                    if len(widgets_values) >= 1:
                        api_inputs["value"] = widgets_values[0]
                elif class_type == "PrimitiveBoolean":
                    if len(widgets_values) >= 1:
                        api_inputs["value"] = widgets_values[0]
                elif class_type in ("VAELoader", "CLIPVisionLoader"):
                    if widgets_values:
                        api_inputs["vae_name" if "VAE" in class_type else "clip_name"] = widgets_values[0]
                elif class_type == "UNETLoader":
                    if len(widgets_values) >= 1:
                        api_inputs["unet_name"] = widgets_values[0]
                    if len(widgets_values) >= 2:
                        api_inputs["weight_dtype"] = widgets_values[1]
                elif class_type == "CLIPLoader":
                    if len(widgets_values) >= 1:
                        api_inputs["clip_name1"] = widgets_values[0]
                    if len(widgets_values) >= 2:
                        api_inputs["clip_name2"] = widgets_values[1]
                    if len(widgets_values) >= 3:
                        api_inputs["type"] = widgets_values[2]
                elif class_type == "CheckpointLoaderSimple":
                    if widgets_values:
                        api_inputs["ckpt_name"] = widgets_values[0]
                elif class_type == "ModelSamplingSD3":
                    if widgets_values:
                        api_inputs["shift"] = widgets_values[0]
                elif class_type in ("GetNode", "SetNode"):
                    # rgthree Get/Set nodes: first widget value is the key
                    if widgets_values:
                        api_inputs["key"] = widgets_values[0]
                else:
                    # Generic fallback: assign by index to numbered inputs
                    for idx, val in enumerate(widgets_values):
                        if isinstance(val, dict):
                            api_inputs[f"param_{idx}"] = str(val)
                        else:
                            api_inputs[f"param_{idx}"] = val
            elif isinstance(widgets_values, dict):
                # VHS nodes use dict widgets
                clean = {k: v for k, v in widgets_values.items()
                         if k not in ("videopreview", "params")}
                api_inputs.update(clean)

        # ── Phase 3: Handle specific node types with known widget structures ──
        # Some nodes put ALL their params in widgets_values list, not in inputs array
        if class_type == "KSampler" and isinstance(widgets_values, list):
            # KSampler: widgets = [seed, control_after_generate, steps, cfg, sampler, scheduler, denoise]
            names = ["seed", "seed_mode", "steps", "cfg", "sampler_name", "scheduler", "denoise"]
            for i, name in enumerate(names):
                if i < len(widgets_values) and name not in api_inputs:
                    api_inputs[name] = widgets_values[i]

        if class_type == "LoraLoaderModelOnly" and isinstance(widgets_values, list):
            if len(widgets_values) >= 1 and "lora_name" not in api_inputs:
                api_inputs["lora_name"] = widgets_values[0]
            if len(widgets_values) >= 2 and "strength_model" not in api_inputs:
                api_inputs["strength_model"] = widgets_values[1]

        if class_type == "WanSCAILToVideo" and isinstance(widgets_values, list):
            names = ["width", "height", "length", "pose_strength"]
            for i, name in enumerate(names):
                if i < len(widgets_values) and name not in api_inputs:
                    api_inputs[name] = widgets_values[i]

        if class_type == "RIFE VFI" and isinstance(widgets_values, list):
            names = ["model", "multiplier", "ensemble", "fast_mode"]
            for i, name in enumerate(names):
                if i < len(widgets_values) and name not in api_inputs:
                    api_inputs[name] = widgets_values[i]

        if class_type == "SCAIL2ColoredMask" and isinstance(widgets_values, list):
            names = ["prompt", "mode", "replacement_mode"]
            for i, name in enumerate(names):
                if i < len(widgets_values) and name not in api_inputs:
                    api_inputs[name] = widgets_values[i]

        if class_type == "ResizeImageMaskNode" and isinstance(widgets_values, list):
            names = ["mode", "scale", "method"]
            for i, name in enumerate(names):
                if i < len(widgets_values) and name not in api_inputs:
                    api_inputs[name] = widgets_values[i]

        if class_type == "CLIPTextEncode" and isinstance(widgets_values, list):
            if len(widgets_values) >= 1 and "text" not in api_inputs:
                api_inputs["text"] = widgets_values[0]

        # ── Add metadata ──
        title = node.get("title", "")
        node_api = {"class_type": class_type, "inputs": api_inputs}
        if title:
            node_api["_meta"] = {"title": title}

        api[str(node_id)] = node_api

    return api


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <workflow_ui.json> [output_api.json]")
        print("  If output not specified, prints to stdout")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    api = convert_to_api(data)

    if len(sys.argv) > 2:
        with open(sys.argv[2], "w") as f:
            json.dump(api, f, indent=2)
        print(f"✅ Converted {len(api)} nodes → {sys.argv[2]}")
    else:
        print(json.dumps(api, indent=2))


if __name__ == "__main__":
    main()
