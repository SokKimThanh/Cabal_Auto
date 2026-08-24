import pytest
import tkinter as tk
from unittest.mock import patch, MagicMock

from ui.components.icon_button import create_icon_label

@pytest.fixture
def tk_root():
    root = tk.Tk()
    yield root
    root.destroy()

def test_create_icon_label_basic(tk_root):
    """Test basic label creation with string text and font/color customizations."""
    label = create_icon_label(
        parent=tk_root,
        icon_name='test_icon',
        text='Test Label',
        icon_fallback='?',
        font=('Arial', 12, 'bold'),
        fg='red',
        bg='blue'
    )

    # In DummyWidget setup string fallback, the label text incorporates the fallback icon
    assert label.cget('text') == '? Test Label' or 'Test Label' in label.cget('text')

    font_val = label.cget('font')
    assert isinstance(font_val, str) or isinstance(font_val, tuple)
    if isinstance(font_val, str):
        assert 'Arial' in font_val and '12' in font_val and 'bold' in font_val
    else:
        assert font_val == ('Arial', 12, 'bold')

    assert label.cget('fg') == 'red'
    assert label.cget('bg') == 'blue'

@patch('ui.components.icon_button.icon_helper')
def test_create_icon_label_icon_only(mock_icon_helper, tk_root):
    """Test label creation without text."""
    # Force string return so it sets 'text' instead of 'image'
    mock_icon_helper.get_icon.return_value = 'M'

    label = create_icon_label(
        parent=tk_root,
        icon_name='monster',
        icon_fallback='M'
    )
    assert label.cget('text') == 'M'

@patch('ui.components.icon_button.icon_helper')
def test_create_icon_label_with_photoimage(mock_icon_helper, tk_root):
    """Test label creation when the icon helper returns a PhotoImage object."""
    # We must use a real PhotoImage for tk.Label creation
    mock_img = tk.PhotoImage(width=1, height=1)
    mock_icon_helper.get_icon.return_value = mock_img

    label = create_icon_label(
        parent=tk_root,
        icon_name='test_icon',
        text='With Image'
    )

    assert str(label.cget('image')) == str(mock_img)
    assert label.cget('compound') == 'left'
    assert label.cget('text') == 'With Image'
    assert hasattr(label, '_icon_ref')
    assert label._icon_ref == mock_img

@patch('ui.components.icon_button.icon_helper')
def test_create_icon_label_with_tooltip(mock_icon_helper, tk_root):
    """Test label creation passing a simple string tooltip text."""
    mock_icon_helper.get_icon.return_value = '?'

    with patch('ui.components.icon_button._attach_simple_tooltip') as mock_attach_tooltip:
        label = create_icon_label(
            parent=tk_root,
            icon_name='info',
            text='Info',
            tooltip_text='This is a tooltip'
        )
        mock_attach_tooltip.assert_called_once_with(label, 'This is a tooltip')

@patch('ui.components.icon_button.icon_helper')
def test_create_icon_label_with_tooltip_key(mock_icon_helper, tk_root):
    """Test label creation passing an i18n tooltip key."""
    mock_icon_helper.get_icon.return_value = '?'

    with patch('ui.components.icon_button.attach_i18n_tooltip') as mock_attach_tooltip:
        label = create_icon_label(
            parent=tk_root,
            icon_name='info',
            text='Info',
            tooltip_key='info_key',
            tooltip_ns='info_ns'
        )
        mock_attach_tooltip.assert_called_once()
        args, kwargs = mock_attach_tooltip.call_args
        assert args[0] == label
        assert args[1] == 'info_key'
        assert kwargs['ns'] == 'info_ns'
        assert 'lang_provider' in kwargs

@patch('ui.components.icon_button.icon_helper')
def test_create_icon_label_icon_only_photoimage(mock_icon_helper, tk_root):
    """Test label creation with an image and empty text."""
    mock_img = tk.PhotoImage(width=1, height=1)
    mock_icon_helper.get_icon.return_value = mock_img

    label = create_icon_label(
        parent=tk_root,
        icon_name='test_icon',
        text='' # No text
    )

    assert str(label.cget('image')) == str(mock_img)

@patch('ui.components.icon_button.icon_helper')
def test_create_icon_label_without_optional_styles(mock_icon_helper, tk_root):
    """Test fallback styles when optional styles are omitted."""
    mock_icon_helper.get_icon.return_value = 'M'

    class MockUIStyle:
        FONT_LABEL = ('Mock Font', 14)
        COLOR_TEXT = '#123456'
        BG_DEFAULT = '#654321'

    with patch.dict('sys.modules', {'lib.ui_style': type('mock_module', (), {'UIStyle': MockUIStyle})}):
        label = create_icon_label(
            parent=tk_root,
            icon_name='test_icon'
        )
        font_val = label.cget('font')
        if isinstance(font_val, str):
            assert 'Mock Font' in font_val and '14' in font_val
        else:
            assert font_val == ('Mock Font', 14)
        assert label.cget('fg') == '#123456'
        assert label.cget('bg') == '#654321'

@patch('ui.components.icon_button.icon_helper')
def test_create_icon_label_import_error(mock_icon_helper, tk_root):
    """Test fallback values when lib.ui_style fails to import."""
    mock_icon_helper.get_icon.return_value = 'M'

    with patch.dict('sys.modules', {'lib.ui_style': None}):
        label = create_icon_label(
            parent=tk_root,
            icon_name='test_icon'
        )
        font_val = label.cget('font')
        if isinstance(font_val, str):
            assert 'Segoe UI' in font_val and '10' in font_val
        else:
            assert font_val == ('Segoe UI', 10)

        assert label.cget('fg') == '#333'
        assert label.cget('bg') == '#FFFFFF'

@patch('ui.components.icon_button.icon_helper')
def test_create_icon_label_with_kwargs(mock_icon_helper, tk_root):
    """Test passing arbitrary kwargs to tk.Label."""
    mock_icon_helper.get_icon.return_value = 'M'

    label = create_icon_label(
        parent=tk_root,
        icon_name='test_icon',
        width=50,
        height=100
    )
    assert label.cget('width') == 50
    assert label.cget('height') == 100
