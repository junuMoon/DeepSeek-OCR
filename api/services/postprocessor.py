"""
Post-processing service for DeepSeek-OCR outputs.

Handles cleaning and formatting of model outputs, including removal of
special tokens and bounding box annotations.
"""

import re
from typing import Optional

from api.core.logging import get_logger

logger = get_logger(__name__)


class OutputPostprocessor:
    """
    Handles post-processing of DeepSeek-OCR model outputs.

    Cleans up special tokens (ref/det tags) and formats the output
    into clean markdown text.
    """

    @staticmethod
    def extract_ref_det_matches(text: str) -> tuple[list, list, list]:
        """
        Extract reference and detection tags from model output.

        Matches patterns like:
        <|ref|>label<|/ref|><|det|>coordinates<|/det|>

        Args:
            text: Raw model output text

        Returns:
            Tuple of (all_matches, image_matches, other_matches)
            - all_matches: List of all (full_match, ref_text, det_text) tuples
            - image_matches: List of full matches containing 'image' label
            - other_matches: List of full matches with non-image labels
        """
        pattern = r'(<\|ref\|>(.*?)<\|/ref\|><\|det\|>(.*?)<\|/det\|>)'
        matches = re.findall(pattern, text, re.DOTALL)

        matches_image = []
        matches_other = []

        for match in matches:
            full_match = match[0]
            if '<|ref|>image<|/ref|>' in full_match:
                matches_image.append(full_match)
            else:
                matches_other.append(full_match)

        return matches, matches_image, matches_other

    @staticmethod
    def clean_markdown(text: str, save_image_refs: bool = False) -> str:
        """
        Clean model output into readable markdown.

        Removes bounding box annotations and special tokens while preserving
        the actual content. Optionally keeps image references.

        Args:
            text: Raw model output with special tokens
            save_image_refs: If True, replace image tags with placeholder markdown

        Returns:
            Cleaned markdown text
        """
        try:
            logger.info("Starting markdown cleaning")

            # Extract all ref/det matches
            matches, matches_image, matches_other = OutputPostprocessor.extract_ref_det_matches(
                text
            )

            cleaned_text = text

            # Handle image references
            if save_image_refs:
                # Replace with markdown image placeholders
                for idx, image_match in enumerate(matches_image):
                    cleaned_text = cleaned_text.replace(
                        image_match, f'![Image {idx}](images/{idx}.jpg)\n'
                    )
                logger.info(f"Replaced {len(matches_image)} image references")
            else:
                # Remove image references entirely
                for image_match in matches_image:
                    cleaned_text = cleaned_text.replace(image_match, '')
                logger.info(f"Removed {len(matches_image)} image references")

            # Remove all other ref/det tags
            for other_match in matches_other:
                cleaned_text = cleaned_text.replace(other_match, '')
            logger.info(f"Removed {len(matches_other)} non-image ref/det tags")

            # Clean up LaTeX symbols
            cleaned_text = (
                cleaned_text.replace('\\coloneqq', ':=').replace('\\eqqcolon', '=:')
            )

            logger.info("Markdown cleaning complete")
            return cleaned_text

        except Exception as e:
            logger.error(f"Failed to clean markdown: {e}", exc_info=True)
            # Return original text if cleaning fails
            return text

    @staticmethod
    def postprocess(
        raw_output: str,
        save_image_refs: bool = False,
        include_raw: bool = False,
    ) -> dict[str, str]:
        """
        Full post-processing pipeline for model output.

        Args:
            raw_output: Raw text from model inference
            save_image_refs: Whether to preserve image references in output
            include_raw: Whether to include raw output in response

        Returns:
            Dictionary with 'text' (cleaned) and optionally 'raw' (original)
        """
        logger.info(f"Post-processing output ({len(raw_output)} chars)")

        # Clean the markdown
        cleaned_text = OutputPostprocessor.clean_markdown(raw_output, save_image_refs)

        result = {"text": cleaned_text}

        if include_raw:
            result["raw"] = raw_output

        logger.info(
            f"Post-processing complete (cleaned: {len(cleaned_text)} chars, "
            f"removed: {len(raw_output) - len(cleaned_text)} chars)"
        )

        return result
